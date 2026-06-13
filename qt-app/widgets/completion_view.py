"""
Auto-ENV — Completion View
Success banner with animated pulse, project path display, and IDE launch button.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget
)


class CompletionView(QWidget):
    """Shown after successful provisioning. Lets the user launch the IDE."""

    launch_requested = pyqtSignal(str, str)   # project_path, ide_name
    new_project_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._project_path = ""
        self._ide_name = "antigravity"
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(20)
        root.addStretch(1)

        # Success banner card
        self._banner = QWidget()
        self._banner.setObjectName("success_banner")
        banner_layout = QVBoxLayout(self._banner)
        banner_layout.setContentsMargins(36, 32, 36, 32)
        banner_layout.setSpacing(10)
        banner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        from qt_app.icons import icon_check, icon_refresh, icon_rocket
        
        self._success_icon_lbl = QLabel()
        self._success_icon_lbl.setObjectName("success_icon")
        self._success_icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._success_icon_lbl.setPixmap(icon_check("#5FDFB4").pixmap(64, 64))
        banner_layout.addWidget(self._success_icon_lbl)

        self._title_lbl = QLabel("Environment Ready!")
        self._title_lbl.setObjectName("success_title")
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setWordWrap(True)
        self._title_lbl.setMinimumHeight(60)
        banner_layout.addWidget(self._title_lbl)

        self._sub_lbl = QLabel("Your isolated environment has been created successfully.")
        self._sub_lbl.setObjectName("success_sub")
        self._sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._sub_lbl.setWordWrap(True)
        self._sub_lbl.setMinimumHeight(40)
        banner_layout.addWidget(self._sub_lbl)

        root.addWidget(self._banner)

        # Project path display
        path_card = QWidget()
        path_card.setObjectName("card_panel")
        path_layout = QVBoxLayout(path_card)
        path_layout.setContentsMargins(16, 12, 16, 12)
        path_layout.setSpacing(4)

        lbl = QLabel("PROJECT LOCATION")
        lbl.setObjectName("section_label")
        path_layout.addWidget(lbl)

        self._path_lbl = QLabel("—")
        self._path_lbl.setWordWrap(True)
        self._path_lbl.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        self._path_lbl.setStyleSheet("font-family: Consolas, monospace; font-size: 12px;")
        path_layout.addWidget(self._path_lbl)
        root.addWidget(path_card)

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        self._new_btn = QPushButton("New Project")
        self._new_btn.setIcon(icon_refresh("#E8E8F0"))
        self._new_btn.setObjectName("secondary_button")
        self._new_btn.clicked.connect(self.new_project_requested)

        self._launch_btn = QPushButton("Open in IDE")
        self._launch_btn.setIcon(icon_rocket("#FFFFFF"))
        self._launch_btn.setObjectName("cta_button")
        self._launch_btn.setMinimumHeight(46)
        self._launch_btn.setMinimumWidth(180)
        self._launch_btn.clicked.connect(self._on_launch)

        btn_row.addWidget(self._new_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._launch_btn)
        root.addLayout(btn_row)
        root.addStretch(1)

    # ── Public API ────────────────────────────────────────────────────────

    def set_result(self, project_path: str, ide_name: str, blueprint: dict) -> None:
        self._project_path = project_path
        self._ide_name = ide_name
        project_name = blueprint.get("project_name", "your project")
        stack = blueprint.get("stack", {})
        lang = stack.get("language", "?")
        fw = stack.get("framework", "?")

        self._title_lbl.setText(f"{project_name} is Ready!")
        self._sub_lbl.setText(
            f"{lang.title()}/{fw.title()} environment provisioned. "
            f"Your .env and dependencies are all set."
        )
        self._path_lbl.setText(project_path)
        self._launch_btn.setText(f"Open in {ide_name.title()}")

    def update_theme(self, dark: bool) -> None:
        from qt_app.icons import icon_check, icon_refresh
        color = "#E8E8F0" if dark else "#1A1A2E"
        success_color = "#5FDFB4" if dark else "#00A878"
        self._success_icon_lbl.setPixmap(icon_check(success_color).pixmap(64, 64))
        self._new_btn.setIcon(icon_refresh(color))

    # ── Slots ─────────────────────────────────────────────────────────────

    def _on_launch(self) -> None:
        if self._project_path:
            self.launch_requested.emit(self._project_path, self._ide_name)
