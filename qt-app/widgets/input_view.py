"""
Auto-ENV — Input View
The first screen: project idea text input, IDE selector, and CTA button.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal, QFileInfo, QSize
from PyQt6.QtGui import QIcon, QPainter
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QSizePolicy,
    QTextEdit, QVBoxLayout, QWidget,
    QFileIconProvider, QStyledItemDelegate, QStyleOptionViewItem
)

class RightIconDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        opt = QStyleOptionViewItem(option)
        opt.features &= ~QStyleOptionViewItem.ViewItemFeature.HasDecoration
        super().paint(painter, opt, index)
        
        icon = index.data(Qt.ItemDataRole.UserRole + 1)
        if isinstance(icon, QIcon) and not icon.isNull():
            # Save painter state to apply smooth transform
            painter.save()
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            icon_size = QSize(20, 20)
            margin = 16
            icon_rect = opt.rect.adjusted(
                opt.rect.width() - icon_size.width() - margin, 
                (opt.rect.height() - icon_size.height()) // 2, 
                -margin, 
                -(opt.rect.height() - icon_size.height()) // 2
            )
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)
            painter.restore()

class IconComboBox(QComboBox):
    def paintEvent(self, event):
        super().paintEvent(event)
        idx = self.currentIndex()
        if idx >= 0:
            icon = self.itemData(idx, Qt.ItemDataRole.UserRole + 1)
            if isinstance(icon, QIcon) and not icon.isNull():
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
                icon_size = QSize(20, 20)
                # Avoid overlapping with the drop-down arrow which is 36px wide per QSS
                margin_right = 44  
                icon_rect = self.rect().adjusted(
                    self.rect().width() - icon_size.width() - margin_right, 
                    (self.rect().height() - icon_size.height()) // 2, 
                    -margin_right, 
                    -(self.rect().height() - icon_size.height()) // 2
                )
                icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)


class InputView(QWidget):
    """Project idea input + IDE selection + 'Prepare Project' button."""

    prepare_requested = pyqtSignal(str, str)   # (prompt_text, ide_name)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    # ── Build ─────────────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 24, 32, 24)
        root.setSpacing(0)

        # ── Hero ──────────────────────────────────────────────────────────
        hero_lbl = QLabel("What are you building?")
        hero_lbl.setObjectName("hero_label")
        hero_lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        root.addWidget(hero_lbl)

        sub_lbl = QLabel("Describe your project and let Auto-ENV configure everything.")
        sub_lbl.setObjectName("sub_label")
        sub_lbl.setWordWrap(True)
        root.addWidget(sub_lbl)
        root.addSpacing(20)

        # ── Text area card ────────────────────────────────────────────────
        input_card = QWidget()
        input_card.setObjectName("card_panel")
        input_card_layout = QVBoxLayout(input_card)
        input_card_layout.setContentsMargins(16, 16, 16, 16)
        input_card_layout.setSpacing(8)

        input_lbl = QLabel("PROJECT IDEA")
        input_lbl.setObjectName("section_label")
        input_card_layout.addWidget(input_lbl)

        self._text_edit = QTextEdit()
        self._text_edit.setPlaceholderText(
            "e.g. A Python FastAPI backend with PostgreSQL, Redis cache, "
            "JWT authentication, and auto-generated OpenAPI docs on port 8000."
        )
        self._text_edit.setMinimumHeight(140)
        self._text_edit.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        input_card_layout.addWidget(self._text_edit)
        root.addWidget(input_card)
        root.addSpacing(16)

        # ── IDE Selector ──────────────────────────────────────────────────
        ide_card = QWidget()
        ide_card.setObjectName("card_panel")
        ide_layout = QVBoxLayout(ide_card)
        ide_layout.setContentsMargins(16, 14, 16, 14)
        ide_layout.setSpacing(10)

        ide_lbl = QLabel("LAUNCH IN IDE")
        ide_lbl.setObjectName("section_label")
        ide_layout.addWidget(ide_lbl)

        self._ide_combo = IconComboBox()
        self._ide_combo.setObjectName("ide_combo")
        self._ide_combo.setMinimumHeight(40)
        self._ide_combo.setItemDelegate(RightIconDelegate(self._ide_combo))
        
        from engine.ide_launcher import discover_installed_ides
        available_ides = discover_installed_ides()
        
        provider = QFileIconProvider()
            
        for label, cmd in available_ides:
            self._ide_combo.addItem(label, cmd)
            idx = self._ide_combo.count() - 1
            if cmd != "explorer":
                file_info = QFileInfo(cmd)
                icon = provider.icon(file_info)
                if not icon.isNull():
                    self._ide_combo.setItemData(idx, icon, Qt.ItemDataRole.UserRole + 1)

        ide_layout.addWidget(self._ide_combo)
        root.addWidget(ide_card)
        root.addSpacing(20)

        # ── CTA button row ────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        
        from qt_app.icons import icon_sparkles
        
        self._cta_btn = QPushButton("Prepare Project")
        self._cta_btn.setIcon(icon_sparkles("#FFFFFF"))
        self._cta_btn.setObjectName("cta_button")
        self._cta_btn.setMinimumHeight(46)
        self._cta_btn.setMinimumWidth(180)
        self._cta_btn.clicked.connect(self._on_prepare)
        btn_row.addWidget(self._cta_btn)
        root.addLayout(btn_row)
        root.addStretch()

    # ── Logic ─────────────────────────────────────────────────────────────

    def _on_prepare(self) -> None:
        text = self._text_edit.toPlainText().strip()
        if not text:
            self._text_edit.setPlaceholderText(
                "⚠  Please describe your project before continuing."
            )
            return
        ide = self._get_selected_ide()
        self.prepare_requested.emit(text, ide)

    def _get_selected_ide(self) -> str:
        return self._ide_combo.currentData()

    def set_loading(self, loading: bool) -> None:
        self._cta_btn.setEnabled(not loading)
        self._cta_btn.setText("Scanning..." if loading else "Prepare Project")

    def reset(self) -> None:
        self._text_edit.clear()
        if self._ide_combo.count() > 0:
            self._ide_combo.setCurrentIndex(0)
        self.set_loading(False)
