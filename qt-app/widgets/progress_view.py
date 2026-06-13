"""
Auto-ENV — Progress View
Real-time terminal log panel with animated spinner and colored status lines.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget
)


# Spinner frames (unicode braille)
_SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

# Log line color maps for HTML terminal rendering
_DARK_COLORS = {
    "[✓]": "#5FDFB4",   # green
    "[→]": "#00D4FF",   # cyan
    "[!]": "#F0B429",   # amber
    "[✗]": "#FF6B6B",   # red
    "   ": "#7090A0",   # muted (subprocess output)
}
_LIGHT_COLORS = {
    "[✓]": "#00A878",
    "[→]": "#0066FF",
    "[!]": "#C07000",
    "[✗]": "#CC2222",
    "   ": "#446080",
}


def _colorize_line(line: str, dark: bool) -> str:
    colors = _DARK_COLORS if dark else _LIGHT_COLORS
    bg = "#080810" if dark else "#1A1A28"
    fg = "#C8E0C8" if dark else "#B8D4B8"

    prefix = line[:3] if len(line) >= 3 else ""
    color = colors.get(prefix, fg)

    # Escape HTML
    safe = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return f'<span style="color:{color};">{safe}</span>'


class ProgressView(QWidget):
    """Animated terminal log panel shown during system scan + provisioning."""

    cancel_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = True
        self._lines: list[str] = []
        self._spinner_idx = 0
        self._spinning = False

        self._spinner_timer = QTimer(self)
        self._spinner_timer.setInterval(80)
        self._spinner_timer.timeout.connect(self._tick_spinner)

        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(12)

        # Title row
        title_row = QHBoxLayout()
        self._title_lbl = QLabel("Setting Up Environment")
        self._title_lbl.setObjectName("hero_label")
        title_row.addWidget(self._title_lbl)
        title_row.addStretch()

        self._spinner_lbl = QLabel("")
        self._spinner_lbl.setObjectName("spinner_label")
        self._spinner_lbl.setMinimumWidth(180)
        self._spinner_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        title_row.addWidget(self._spinner_lbl)
        root.addLayout(title_row)

        sub = QLabel("Please wait while Auto-ENV builds your isolated environment.")
        sub.setObjectName("sub_label")
        sub.setWordWrap(True)
        root.addWidget(sub)

        # Terminal card
        term_card = QWidget()
        term_card.setObjectName("card_panel")
        term_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout = QVBoxLayout(term_card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        term_hdr = QLabel("LIVE OUTPUT")
        term_hdr.setObjectName("section_label")
        term_hdr.setContentsMargins(16, 12, 16, 4)
        card_layout.addWidget(term_hdr)

        self._log_area = QTextEdit()
        self._log_area.setObjectName("terminal_log")
        self._log_area.setReadOnly(True)
        self._log_area.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        card_layout.addWidget(self._log_area)
        root.addWidget(term_card, stretch=1)

        # Cancel button (bottom)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        from qt_app.icons import icon_x
        self._cancel_btn = QPushButton("Cancel")
        self._cancel_btn.setIcon(icon_x("#E8E8F0"))
        self._cancel_btn.setObjectName("secondary_button")
        self._cancel_btn.clicked.connect(self.cancel_requested)
        btn_row.addWidget(self._cancel_btn)
        root.addLayout(btn_row)

    # ── Public API ────────────────────────────────────────────────────────

    def clear(self) -> None:
        self._lines.clear()
        self._log_area.clear()

    def append_log(self, text: str) -> None:
        """Append a log line and auto-scroll."""
        self._lines.append(text)
        colored = _colorize_line(text, self._dark)
        self._log_area.append(colored)
        # Auto-scroll to bottom
        sb = self._log_area.verticalScrollBar()
        sb.setValue(sb.maximum())

    def start_spinner(self, label: str = "Working") -> None:
        self._spinning = True
        self._spinner_label_text = label
        self._spinner_timer.start()

    def stop_spinner(self) -> None:
        self._spinning = False
        self._spinner_timer.stop()
        self._spinner_lbl.setText("")

    def set_title(self, title: str) -> None:
        self._title_lbl.setText(title)

    def set_cancel_enabled(self, enabled: bool) -> None:
        self._cancel_btn.setEnabled(enabled)
        self._cancel_btn.setVisible(enabled)

    def update_theme(self, dark: bool) -> None:
        self._dark = dark
        
        from qt_app.icons import icon_x
        color = "#E8E8F0" if dark else "#1A1A2E"
        self._cancel_btn.setIcon(icon_x(color))
        
        # Re-render all existing lines
        self._log_area.clear()
        bg = "#080810" if dark else "#1A1A28"
        for line in self._lines:
            colored = _colorize_line(line, dark)
            self._log_area.append(colored)

    # ── Spinner ───────────────────────────────────────────────────────────

    def _tick_spinner(self) -> None:
        if not self._spinning:
            return
        frame = _SPINNER_FRAMES[self._spinner_idx % len(_SPINNER_FRAMES)]
        self._spinner_lbl.setText(f"{frame}  {self._spinner_label_text}...")
        self._spinner_idx += 1
