"""
Auto-ENV — Blueprint View
Displays the Gemini-generated JSON blueprint and lets the user approve execution.
"""

from __future__ import annotations

import json

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QTextCharFormat, QFont
from PyQt6.QtWidgets import (
    QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QTextEdit, QVBoxLayout, QWidget
)


def _colorize_json(text: str, dark: bool = True) -> str:
    """Return a basic HTML-colored JSON string for display."""
    import re
    html = text
    # Escape HTML first
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    key_color   = "#00D4FF" if dark else "#0066FF"
    str_color   = "#98C379" if dark else "#2A8A3C"
    num_color   = "#E5C07B" if dark else "#A05C00"
    bool_color  = "#C678DD" if dark else "#8800CC"
    null_color  = "#7F848E" if dark else "#888888"
    brace_color = "#ABB2BF" if dark else "#444444"

    # Keys
    html = re.sub(
        r'"([^"]+)"(\s*:)',
        rf'<span style="color:{key_color}">&quot;\1&quot;</span>\2',
        html,
    )
    # String values (after colon)
    html = re.sub(
        r':\s*"([^"]*)"',
        rf': <span style="color:{str_color}">&quot;\1&quot;</span>',
        html,
    )
    # Numbers
    html = re.sub(
        r':\s*(-?\d+\.?\d*)',
        rf': <span style="color:{num_color}">\1</span>',
        html,
    )
    # Booleans and null
    html = re.sub(
        r'\b(true|false)\b',
        rf'<span style="color:{bool_color}">\1</span>',
        html,
    )
    html = re.sub(
        r'\bnull\b',
        rf'<span style="color:{null_color}">null</span>',
        html,
    )

    bg = "#080810" if dark else "#1A1A28"
    return (
        f'<pre style="background:{bg}; color:#ABB2BF; '
        f'font-family: Consolas,monospace; font-size:12px; '
        f'margin:0; padding:10px; line-height:1.5;">'
        f'{html}</pre>'
    )


class BlueprintView(QWidget):
    """Shows JSON blueprint + Approve / Back buttons."""

    approved = pyqtSignal()
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dark = True
        self._blueprint: dict = {}
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(14)

        # Title
        title = QLabel("Configuration Blueprint")
        title.setObjectName("hero_label")
        root.addWidget(title)

        sub = QLabel("Review the generated environment blueprint before executing.")
        sub.setObjectName("sub_label")
        sub.setWordWrap(True)
        root.addWidget(sub)

        # Summary strip
        self._summary_row = QHBoxLayout()
        self._summary_row.setSpacing(20)
        for attr in ("stack_lbl", "port_lbl", "deps_lbl"):
            lbl = QLabel("—")
            lbl.setObjectName("section_label")
            setattr(self, attr, lbl)
            self._summary_row.addWidget(lbl)
        self._summary_row.addStretch()
        root.addLayout(self._summary_row)

        # Execution Graph
        from qt_app.graph_view import GraphView
        self._graph_view = GraphView()
        root.addWidget(self._graph_view)

        # JSON card
        json_card = QWidget()
        json_card.setObjectName("card_panel")
        json_card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        card_layout = QVBoxLayout(json_card)
        card_layout.setContentsMargins(0, 0, 0, 0)

        section_lbl = QLabel("BLUEPRINT JSON")
        section_lbl.setObjectName("section_label")
        section_lbl.setContentsMargins(16, 12, 16, 4)
        card_layout.addWidget(section_lbl)

        self._json_display = QTextEdit()
        self._json_display.setObjectName("terminal_log")
        self._json_display.setReadOnly(True)
        self._json_display.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        card_layout.addWidget(self._json_display)
        root.addWidget(json_card, stretch=1)

        # Buttons
        btn_row = QHBoxLayout()
        
        from qt_app.icons import icon_arrow_left, icon_check
        self._back_btn = QPushButton("Back")
        self._back_btn.setIcon(icon_arrow_left("#E8E8F0"))
        self._back_btn.setObjectName("secondary_button")
        self._back_btn.clicked.connect(self.back_requested)

        self._approve_btn = QPushButton("Approve & Execute")
        self._approve_btn.setIcon(icon_check("#FFFFFF"))
        self._approve_btn.setObjectName("approve_button")
        self._approve_btn.setMinimumHeight(46)
        self._approve_btn.clicked.connect(self.approved)

        btn_row.addWidget(self._back_btn)
        btn_row.addStretch()
        btn_row.addWidget(self._approve_btn)
        root.addLayout(btn_row)

    # ── Data ──────────────────────────────────────────────────────────────

    def set_blueprint(self, blueprint: dict, dark: bool = True) -> None:
        self._blueprint = blueprint
        self._dark = dark
        self._refresh_display()

    def _refresh_display(self) -> None:
        b = self._blueprint
        stack = b.get("stack", {})
        lang = stack.get("language", "?")
        fw = stack.get("framework", "?")
        port = b.get("env_vars", {}).get("PORT", "?")
        n_deps = len(b.get("dependencies", []))

        self.stack_lbl.setText(f"STACK  {lang.upper()}/{fw.upper()}")
        self.port_lbl.setText(f"PORT  {port}")
        self.deps_lbl.setText(f"DEPS  {n_deps}")

        pretty = json.dumps(self._blueprint, indent=2)
        self._json_display.setHtml(_colorize_json(pretty, self._dark))
        self._graph_view.set_blueprint(self._blueprint, self._dark)

    def update_theme(self, dark: bool) -> None:
        self._dark = dark
        from qt_app.icons import icon_arrow_left
        color = "#E8E8F0" if dark else "#1A1A2E"
        self._back_btn.setIcon(icon_arrow_left(color))
        
        if self._blueprint:
            self._refresh_display()
