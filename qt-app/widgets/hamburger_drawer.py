"""
Auto-ENV — Hamburger Side Drawer
Animated slide-out panel from the right edge of the main window.
Contains a dark mode toggle switch.
"""

from __future__ import annotations

from PyQt6.QtCore import (
    QEasingCurve, QPropertyAnimation, QRect, Qt, pyqtSignal
)
from PyQt6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget
)
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import pyqtProperty, QRectF

class ToggleSwitch(QWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, parent=None, checked=False):
        super().__init__(parent)
        self.setFixedSize(40, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._checked = checked
        self._position = 1.0 if checked else 0.0
        self._anim = QPropertyAnimation(self, b"position")
        self._anim.setDuration(150)
        self._dark = True

    def isChecked(self) -> bool:
        return self._checked

    def setChecked(self, checked: bool) -> None:
        if self._checked != checked:
            self._checked = checked
            self.toggled.emit(checked)
            self._anim.stop()
            self._anim.setEndValue(1.0 if checked else 0.0)
            self._anim.start()

    def mouseReleaseEvent(self, e) -> None:
        if e.button() == Qt.MouseButton.LeftButton:
            self.setChecked(not self._checked)

    def set_dark(self, dark: bool) -> None:
        self._dark = dark
        self.update()

    @pyqtProperty(float)
    def position(self) -> float:
        return self._position

    @position.setter
    def position(self, pos: float) -> None:
        self._position = pos
        self.update()

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        if self._dark:
            bg_color = QColor("#00D4FF") if self._checked else QColor("#3A3A55")
            thumb_color = QColor("#FFFFFF") if self._checked else QColor("#C8C8E0")
        else:
            bg_color = QColor("#0066FF") if self._checked else QColor("#D0D8E8")
            thumb_color = QColor("#FFFFFF")

        # Draw track
        rect = QRectF(0, 0, self.width(), self.height())
        p.setPen(Qt.PenStyle.NoPen)
        p.setBrush(QBrush(bg_color))
        p.drawRoundedRect(rect, self.height() / 2, self.height() / 2)

        # Draw thumb
        thumb_r = self.height() - 6
        x = 3 + (self.width() - thumb_r - 6) * self._position
        y = 3
        p.setBrush(QBrush(thumb_color))
        p.drawEllipse(QRectF(x, y, thumb_r, thumb_r))



class SideDrawer(QWidget):
    """
    A slide-in/out overlay drawer that appears from the right side of a parent widget.
    It does NOT use a separate window — it is parented to the main window and
    repositioned over it on demand.
    """

    theme_toggled = pyqtSignal(bool)   # True → dark
    change_api_key_requested = pyqtSignal()

    _DRAWER_WIDTH = 240

    def __init__(self, parent: QWidget, dark: bool = True):
        super().__init__(parent)
        self._dark = dark
        self._visible = False
        self._anim = QPropertyAnimation(self, b"geometry")
        self._anim.setDuration(220)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_anim_finished)

        self.setObjectName("side_drawer")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self._build_ui()
        self.hide()

    def _on_anim_finished(self):
        if not self._visible:
            self.hide()

    # ── Build ────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Title row
        title_row = QHBoxLayout()
        title_lbl = QLabel("Settings")
        title_lbl.setObjectName("drawer_title")
        # Close button
        from qt_app.icons import icon_x
        close_btn = QPushButton("Close")
        close_btn.setIcon(icon_x("#E8E8F0"))
        close_btn.setObjectName("secondary_button")
        close_btn.clicked.connect(self.close_drawer)
        title_row.addWidget(title_lbl)
        title_row.addStretch()
        title_row.addWidget(close_btn)
        layout.addLayout(title_row)

        # Divider line
        divider = QWidget()
        divider.setFixedHeight(1)
        divider.setStyleSheet("background: rgba(128,128,200,0.2);")
        layout.addWidget(divider)

        # Dark Mode toggle
        toggle_row = QHBoxLayout()
        toggle_lbl = QLabel("Dark Mode")
        toggle_lbl.setStyleSheet("font-size: 13px;")
        self._toggle = ToggleSwitch(checked=self._dark)
        self._toggle.setObjectName("dark_mode_toggle")
        self._toggle.set_dark(self._dark)
        self._toggle.toggled.connect(self._on_toggle)
        toggle_row.addWidget(toggle_lbl)
        toggle_row.addStretch()
        toggle_row.addWidget(self._toggle)
        layout.addLayout(toggle_row)

        # API Key Button
        api_key_row = QHBoxLayout()
        api_key_btn = QPushButton("Update API Key")
        api_key_btn.setObjectName("secondary_button")
        api_key_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        api_key_btn.clicked.connect(self.change_api_key_requested.emit)
        api_key_row.addWidget(api_key_btn)
        layout.addLayout(api_key_row)

        layout.addStretch()

        # Version info
        ver_lbl = QLabel("Auto-ENV v1.0")
        ver_lbl.setStyleSheet("color: rgba(128,128,200,0.5); font-size: 11px;")
        layout.addWidget(ver_lbl, alignment=Qt.AlignmentFlag.AlignCenter)

    # ── Slot ─────────────────────────────────────────────────────────────

    def update_theme(self, dark: bool) -> None:
        self._dark = dark
        self.theme_toggled.emit(dark)

    def _on_toggle(self, checked: bool) -> None:
        self.update_theme(checked)

    def set_dark(self, dark: bool) -> None:
        """Sync toggle state from external theme change."""
        self._toggle.blockSignals(True)
        self._toggle.setChecked(dark)
        self._toggle.set_dark(dark)
        self._toggle.blockSignals(False)
        self._dark = dark

    # ── Animation ────────────────────────────────────────────────────────

    def _recompute_geometry(self) -> tuple[QRect, QRect]:
        parent = self.parentWidget()
        pw = parent.width()
        ph = parent.height()
        header_h = 52
        dw = self._DRAWER_WIDTH
        dh = ph - header_h

        closed = QRect(pw, header_h, dw, dh)
        opened = QRect(pw - dw, header_h, dw, dh)
        return closed, opened

    def open_drawer(self) -> None:
        if self._visible:
            return
        self._visible = True
        closed, opened = self._recompute_geometry()
        self.setGeometry(closed)
        self.show()
        self.raise_()
        self._anim.stop()
        self._anim.setStartValue(closed)
        self._anim.setEndValue(opened)
        self._anim.start()

    def close_drawer(self) -> None:
        if not self._visible:
            return
        self._visible = False
        closed, opened = self._recompute_geometry()
        self._anim.stop()
        self._anim.setStartValue(opened)
        self._anim.setEndValue(closed)
        self._anim.start()

    def toggle_drawer(self) -> None:
        if self._visible:
            self.close_drawer()
        else:
            self.open_drawer()

    def resizeEvent(self, event) -> None:
        """Re-snap drawer position when parent window is resized."""
        super().resizeEvent(event)
        if self._visible:
            _, opened = self._recompute_geometry()
            self.setGeometry(opened)
