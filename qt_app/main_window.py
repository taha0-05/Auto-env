"""
Auto-ENV — Main Window
QMainWindow with header bar, hamburger drawer, QStackedWidget views,
and full multi-threaded worker orchestration.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QStackedWidget, QVBoxLayout, QWidget, QMessageBox,
    QFileDialog
)

# Workers
from qt_app.workers.scan_worker import ScanThread
from qt_app.workers.gemini_worker import GeminiThread
from qt_app.workers.provision_worker import ProvisionThread

# Widgets
from qt_app.widgets.hamburger_drawer import SideDrawer
from qt_app.widgets.input_view import InputView
from qt_app.widgets.blueprint_view import BlueprintView
from qt_app.widgets.progress_view import ProgressView
from qt_app.widgets.completion_view import CompletionView

# Themes
from qt_app.themes import get_qss

# Engine
from engine.gemini_client import has_api_key, save_api_key


# View indices
_VIEW_INPUT      = 0
_VIEW_BLUEPRINT  = 1
_VIEW_PROGRESS   = 2
_VIEW_COMPLETION = 3


# ---------------------------------------------------------------------------
# API Key Dialog
# ---------------------------------------------------------------------------

class ApiKeyDialog(QDialog):
    """Prompt the user for their Gemini API key."""

    def __init__(self, parent=None, is_update=False):
        super().__init__(parent)
        self.setWindowTitle("Gemini API Key")
        self.setMinimumWidth(420)
        self.setObjectName("card_panel")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title_lbl = QLabel("Update API Key" if is_update else "API Key Required")
        title_lbl.setObjectName("hero_label")
        layout.addWidget(title_lbl)

        desc_lbl = QLabel(
            "Auto-ENV needs a Gemini API key to generate environment blueprints.\n"
            "Get your free key at: <a href='https://aistudio.google.com/app/apikey' style='color:#00D4FF;'>aistudio.google.com</a>"
        )
        desc_lbl.setObjectName("sub_label")
        desc_lbl.setOpenExternalLinks(True)
        layout.addWidget(desc_lbl)

        self._key_input = QLineEdit()
        self._key_input.setPlaceholderText("Paste your GEMINI_API_KEY here...")
        self._key_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self._key_input)

        self._save_cb_lbl = QLabel("Key will be saved to ~/.autoenv/gemini_key.txt")
        self._save_cb_lbl.setStyleSheet("font-size: 11px; color: #7070A0;")
        layout.addWidget(self._save_cb_lbl)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondary_button")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        
        save_btn = QPushButton("Save Key")
        save_btn.setObjectName("cta_button")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)

        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        layout.addLayout(btn_layout)

    def get_key(self) -> str:
        return self._key_input.text().strip()


# ---------------------------------------------------------------------------
# Header Bar Widget
# ---------------------------------------------------------------------------

class HeaderBar(QWidget):
    hamburger_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("header_bar")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 12, 0)

        # App title — ALWAYS "Auto-ENV"
        self._title = QLabel("Auto-ENV")
        self._title.setObjectName("app_title")
        layout.addWidget(self._title)

        layout.addStretch()

        # Hamburger button
        self._btn = QPushButton()
        self._btn.setObjectName("hamburger_btn")
        self._btn.setFixedSize(38, 38)
        self._btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._btn.clicked.connect(self.hamburger_clicked)
        layout.addWidget(self._btn)

    def update_theme(self, dark: bool) -> None:
        from qt_app.icons import icon_hamburger
        color = "#E8E8F0" if dark else "#1A1A2E"
        self._btn.setIcon(icon_hamburger(color))


# ---------------------------------------------------------------------------
# Main Window
# ---------------------------------------------------------------------------

class MainWindow(QMainWindow):
    """
    Primary application window.
    Title is immutably set to "Auto-ENV" and never changed by any theme operation.
    """

    def __init__(self):
        super().__init__()
        # ── Window setup ──────────────────────────────────────────────────
        self.setWindowTitle("Auto-ENV")
        self.setMinimumSize(700, 500)
        self.resize(900, 640)

        # State
        self._dark_mode = True
        self._system_info: dict = {}
        self._blueprint: dict = {}
        self._selected_ide = "antigravity"
        self._project_path = ""
        self._prompt_text = ""
        self._session_start: float = 0.0

        # Active worker threads (kept as instance attrs to prevent GC)
        self._scan_thread: ScanThread | None = None
        self._gemini_thread: GeminiThread | None = None
        self._provision_thread: ProvisionThread | None = None

        self._build_ui()
        self._apply_theme()

    # ── UI Construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        # Central widget
        central = QWidget()
        central.setObjectName("central_widget")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header
        self._header = HeaderBar(central)
        self._header.hamburger_clicked.connect(self._toggle_drawer)
        root_layout.addWidget(self._header)

        # Stacked views
        self._stack = QStackedWidget()
        self._stack.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        root_layout.addWidget(self._stack)

        # Instantiate views
        self._input_view = InputView()
        self._blueprint_view = BlueprintView()
        self._progress_view = ProgressView()
        self._completion_view = CompletionView()

        self._stack.addWidget(self._input_view)        # 0
        self._stack.addWidget(self._blueprint_view)    # 1
        self._stack.addWidget(self._progress_view)     # 2
        self._stack.addWidget(self._completion_view)   # 3

        # Side drawer (overlay — parented to central widget)
        self._drawer = SideDrawer(central, dark=self._dark_mode)
        self._drawer.theme_toggled.connect(self._on_theme_toggled)
        self._drawer.change_api_key_requested.connect(self._on_change_api_key)

        # Connect view signals
        self._input_view.prepare_requested.connect(self._on_prepare_requested)
        self._blueprint_view.approved.connect(self._on_blueprint_approved)
        self._blueprint_view.back_requested.connect(lambda: self._show_view(_VIEW_INPUT))
        self._progress_view.cancel_requested.connect(self._on_cancel)
        self._completion_view.launch_requested.connect(self._on_launch_ide)
        self._completion_view.new_project_requested.connect(self._on_new_project)

        # Show input view first
        self._show_view(_VIEW_INPUT)

    # ── Theme ─────────────────────────────────────────────────────────────

    def _apply_theme(self) -> None:
        self.setStyleSheet(get_qss(self._dark_mode))
        # NEVER overwrite window title
        # (setStyleSheet does not affect windowTitle, but this is a safeguard)
        assert self.windowTitle() == "Auto-ENV"

        self._blueprint_view.update_theme(self._dark_mode)
        self._progress_view.update_theme(self._dark_mode)
        self._completion_view.update_theme(self._dark_mode)
        self._header.update_theme(self._dark_mode)
        self._drawer.set_dark(self._dark_mode)

    def _on_theme_toggled(self, dark: bool) -> None:
        self._dark_mode = dark
        self._apply_theme()
        # Drawer stays open — just re-style. Title is never touched.

    def _on_change_api_key(self) -> None:
        self._drawer.close_drawer()
        dlg = ApiKeyDialog(self, is_update=True)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            api_key = dlg.get_key()
            if api_key:
                save_api_key(api_key)
                QMessageBox.information(self, "Auto-ENV", "API Key updated successfully.")

    # ── Drawer ────────────────────────────────────────────────────────────

    def _toggle_drawer(self) -> None:
        self._drawer.toggle_drawer()

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        # Keep drawer anchored to the right edge of the central widget
        if hasattr(self, "_drawer"):
            self._drawer.raise_()

    # ── View Navigation ───────────────────────────────────────────────────

    def _show_view(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        if hasattr(self, "_drawer") and self._drawer._visible:
            self._drawer.close_drawer()

    # ── Scan Phase ────────────────────────────────────────────────────────

    def _on_prepare_requested(self, prompt: str, ide: str) -> None:
        self._prompt_text = prompt
        self._selected_ide = ide
        self._session_start = time.monotonic()

        # Switch to progress view and start scan
        self._progress_view.clear()
        self._progress_view.set_title("Scanning System")
        self._progress_view.set_cancel_enabled(False)
        self._show_view(_VIEW_PROGRESS)

        self._progress_view.start_spinner("Probing system")
        self._progress_view.append_log("[→] Starting system scan...")

        self._input_view.set_loading(True)

        self._scan_thread = ScanThread(self)
        self._scan_thread.log.connect(self._progress_view.append_log)
        self._scan_thread.finished.connect(self._on_scan_finished)
        self._scan_thread.error.connect(self._on_scan_error)
        self._scan_thread.start()

    def _on_scan_finished(self, system_info: dict) -> None:
        self._system_info = system_info
        self._progress_view.stop_spinner()
        self._progress_view.append_log("[✓] System scan complete. Calling Gemini AI...")
        self._start_gemini_call()

    def _on_scan_error(self, msg: str) -> None:
        self._progress_view.stop_spinner()
        self._progress_view.append_log(f"[!] Scan warning: {msg}")
        self._progress_view.append_log("[→] Continuing with partial system info...")
        self._start_gemini_call()

    # ── Gemini Phase ──────────────────────────────────────────────────────

    def _start_gemini_call(self) -> None:
        # Check API key
        # Load API key via env var → config file fallback
        import os as _os
        from pathlib import Path as _Path
        _key_file = _Path.home() / ".autoenv" / "gemini_key.txt"
        api_key = _os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key and _key_file.exists():
            api_key = _key_file.read_text(encoding="utf-8").strip()
        if not api_key:
            dlg = ApiKeyDialog(self)
            if dlg.exec() == QDialog.DialogCode.Accepted:
                api_key = dlg.get_key()
                if api_key:
                    save_api_key(api_key)
                else:
                    self._abort("No API key provided. Cannot call Gemini.")
                    return
            else:
                self._abort("API key entry cancelled.")
                return

        self._progress_view.start_spinner("Generating blueprint")

        self._gemini_thread = GeminiThread(
            self._prompt_text, self._system_info, api_key, parent=self
        )
        self._gemini_thread.log.connect(self._progress_view.append_log)
        self._gemini_thread.finished.connect(self._on_gemini_finished)
        self._gemini_thread.error.connect(self._on_gemini_error)
        self._gemini_thread.start()

    def _on_gemini_finished(self, blueprint: dict) -> None:
        self._blueprint = blueprint
        self._progress_view.stop_spinner()
        self._progress_view.append_log("[✓] Blueprint generated successfully!")

        # Show blueprint review
        self._blueprint_view.set_blueprint(blueprint, self._dark_mode)
        self._input_view.set_loading(False)
        self._show_view(_VIEW_BLUEPRINT)

    def _on_gemini_error(self, msg: str) -> None:
        self._progress_view.stop_spinner()
        self._abort(f"Gemini API error:\n\n{msg}")

    # ── Provision Phase ───────────────────────────────────────────────────

    def _on_blueprint_approved(self) -> None:
        # Choose base path
        base_path = str(Path.home() / "AutoENV-Projects")
        Path(base_path).mkdir(parents=True, exist_ok=True)

        # Switch to progress for provisioning
        self._progress_view.clear()
        self._progress_view.set_title("Provisioning Environment")
        self._progress_view.set_cancel_enabled(True)
        self._show_view(_VIEW_PROGRESS)
        self._progress_view.start_spinner("Installing dependencies")
        self._progress_view.append_log(f"[→] Base directory: {base_path}")

        self._provision_thread = ProvisionThread(self._blueprint, base_path, parent=self)
        self._provision_thread.log.connect(self._progress_view.append_log)
        self._provision_thread.finished.connect(self._on_provision_finished)
        self._provision_thread.error.connect(self._on_provision_error)
        self._provision_thread.start()

    def _on_provision_finished(self, success: bool, project_path: str) -> None:
        self._progress_view.stop_spinner()
        self._progress_view.set_cancel_enabled(False)

        if success and project_path:
            self._project_path = project_path
            self._log_session(success=True)
            self._completion_view.set_result(
                project_path, self._selected_ide, self._blueprint
            )
            self._show_view(_VIEW_COMPLETION)
        else:
            self._log_session(success=False)
            # Stay on progress view, show error inline
            self._progress_view.append_log("[!] Provisioning did not complete. Check logs above.")

    def _on_provision_error(self, msg: str) -> None:
        self._progress_view.stop_spinner()
        self._log_session(success=False, error=msg)
        QMessageBox.critical(self, "Provisioning Error", msg)

    # ── IDE Launch ────────────────────────────────────────────────────────

    def _on_launch_ide(self, project_path: str, ide_cmd: str) -> None:
        from engine.ide_launcher import launch_ide
        self._progress_view.clear()
        self._progress_view.set_title("Launching IDE")
        self._progress_view.set_cancel_enabled(False)
        # Don't switch view; just do it
        launched = launch_ide(
            ide_cmd,
            project_path,
            self._blueprint,
            log_fn=self._progress_view.append_log,
        )
        if not launched:
            QMessageBox.information(
                self,
                "IDE Not Found",
                f"'{self._selected_ide}' was not found in PATH.\n"
                "Your project folder has been opened in the file explorer instead.",
            )

    # ── Cancel ────────────────────────────────────────────────────────────

    def _on_cancel(self) -> None:
        if self._provision_thread and self._provision_thread.isRunning():
            self._provision_thread.cancel()
            self._progress_view.append_log("[!] Cancellation requested...")
        elif self._gemini_thread and self._gemini_thread.isRunning():
            self._gemini_thread.terminate()
            self._progress_view.append_log("[!] Gemini request cancelled.")
            self._abort("Operation cancelled by user.")

    def _abort(self, message: str) -> None:
        self._progress_view.stop_spinner()
        self._input_view.set_loading(False)
        QMessageBox.warning(self, "Auto-ENV", message)
        self._show_view(_VIEW_INPUT)

    # ── New Project ───────────────────────────────────────────────────────

    def _on_new_project(self) -> None:
        self._input_view.reset()
        self._blueprint = {}
        self._project_path = ""
        self._progress_view.clear()
        self._show_view(_VIEW_INPUT)

    # ── Session Logger ────────────────────────────────────────────────────

    def _log_session(self, success: bool, error: str = "") -> None:
        try:
            from engine.session_logger import append_session
            duration = time.monotonic() - self._session_start
            stack = self._blueprint.get("stack", {})
            port = None
            try:
                port = int(self._blueprint.get("env_vars", {}).get("PORT", 0)) or None
            except (ValueError, TypeError):
                pass
            append_session(
                prompt=self._prompt_text,
                stack=stack,
                assigned_port=port,
                project_path=self._project_path,
                success=success,
                duration_seconds=duration,
                error_message=error,
            )
        except Exception:
            pass   # Logging must never crash the app

    # ── Cleanup ───────────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        # Terminate any running threads gracefully
        for t in (self._scan_thread, self._gemini_thread, self._provision_thread):
            if t and t.isRunning():
                t.quit()
                t.wait(2000)
        super().closeEvent(event)
