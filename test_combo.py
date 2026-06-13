import sys
from PyQt6.QtWidgets import QApplication, QComboBox, QStyledItemDelegate, QWidget, QVBoxLayout, QFileIconProvider, QStyleOptionViewItem, QStyle
from PyQt6.QtCore import Qt, QFileInfo, QSize
from PyQt6.QtGui import QIcon, QPainter

class RightIconDelegate(QStyledItemDelegate):
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        # Draw the background/selection first using default behavior
        super().paint(painter, option, index)
        
        # Get the icon from the model
        icon = index.data(Qt.ItemDataRole.DecorationRole)
        if isinstance(icon, QIcon) and not icon.isNull():
            # Calculate where to draw the icon (right side)
            icon_size = option.decorationSize
            if icon_size.isEmpty():
                icon_size = QSize(16, 16)
            
            # Draw on the right with a margin
            margin = 8
            rect = option.rect
            icon_rect = rect.adjusted(rect.width() - icon_size.width() - margin, 
                                      (rect.height() - icon_size.height()) // 2, 
                                      -margin, 
                                      -(rect.height() - icon_size.height()) // 2)
            
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)

app = QApplication(sys.argv)
w = QWidget()
layout = QVBoxLayout(w)

combo = QComboBox()
# To prevent the default drawing of the icon on the left, we might need to NOT set DecorationRole,
# but rather a custom role, or we just let it draw on the left as well?
# Better: use a custom role for the icon!
ICON_ROLE = Qt.ItemDataRole.UserRole + 1

class CustomDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        # Don't let base class draw the icon, but draw text and background
        option_copy = QStyleOptionViewItem(option)
        option_copy.features &= ~QStyleOptionViewItem.ViewItemFeature.HasDecoration
        super().paint(painter, option_copy, index)
        
        icon = index.data(ICON_ROLE)
        if isinstance(icon, QIcon) and not icon.isNull():
            icon_size = option.decorationSize
            if icon_size.isEmpty():
                icon_size = QSize(24, 24)
            margin = 12
            icon_rect = option.rect.adjusted(option.rect.width() - icon_size.width() - margin, 
                                             (option.rect.height() - icon_size.height()) // 2, 
                                             -margin, 
                                             -(option.rect.height() - icon_size.height()) // 2)
            icon.paint(painter, icon_rect, Qt.AlignmentFlag.AlignCenter)

combo.setItemDelegate(CustomDelegate())

provider = QFileIconProvider()
file_info = QFileInfo("C:\\Windows\\System32\\cmd.exe")
icon = provider.icon(file_info)

combo.addItem("Command Prompt", "cmd.exe")
combo.setItemData(0, icon, ICON_ROLE)

layout.addWidget(combo)
w.show()

# Instead of exec, just test if it compiles and runs for a second
# sys.exit(app.exec())
print("Test compiled and ran successfully")
