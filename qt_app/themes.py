"""
Auto-ENV — QSS Theme Stylesheets
Provides full dark and light mode palettes for all PyQt6 widgets.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# DARK THEME
# ---------------------------------------------------------------------------
DARK_QSS = """
/* ── Root / Window ────────────────────────────────────────────────────── */
QMainWindow, QWidget#central_widget {
    background-color: #121214;
}

QWidget {
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #E8E8F0;
    background-color: transparent;
}

/* ── Header / Toolbar strip ───────────────────────────────────────────── */
QWidget#header_bar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #1A1A2E, stop:1 #16213E);
    border-bottom: 1px solid #2A2A45;
    min-height: 52px;
    max-height: 52px;
}

QLabel#app_title {
    color: #FFFFFF;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* ── Hamburger Button ─────────────────────────────────────────────────── */
QPushButton#hamburger_btn {
    background: transparent;
    border: none;
    color: #A0A0C0;
    font-size: 20px;
    padding: 4px 10px;
    border-radius: 6px;
}
QPushButton#hamburger_btn:hover {
    background: rgba(0, 212, 255, 0.12);
    color: #00D4FF;
}
QPushButton#hamburger_btn:pressed {
    background: rgba(0, 212, 255, 0.22);
}

/* ── Side Drawer ──────────────────────────────────────────────────────── */
QWidget#side_drawer {
    background: #1E1E2E;
    border-left: 1px solid #2A2A45;
}

QLabel#drawer_title {
    color: #00D4FF;
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

QCheckBox#dark_mode_toggle {
    color: #C8C8E0;
    font-size: 13px;
    spacing: 10px;
}
QCheckBox#dark_mode_toggle::indicator {
    width: 40px;
    height: 22px;
    border-radius: 11px;
    background-color: #3A3A55;
    border: 1px solid #5A5A80;
}
QCheckBox#dark_mode_toggle::indicator:checked {
    background-color: #00D4FF;
    border-color: #00D4FF;
}

/* ── Panel Cards ──────────────────────────────────────────────────────── */
QWidget#card_panel {
    background: #16161C;
    border: 1px solid #2A2A35;
    border-radius: 12px;
}

/* ── Section Labels ───────────────────────────────────────────────────── */
QLabel#section_label {
    color: #00D4FF;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

QLabel#hero_label {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 700;
}

QLabel#sub_label {
    color: #7070A0;
    font-size: 13px;
}

/* ── Text Inputs ──────────────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #0D0D12;
    color: #E8E8F0;
    border: 1px solid #2A2A40;
    border-radius: 8px;
    padding: 10px;
    selection-background-color: #00D4FF40;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #00D4FF;
    background-color: #0F0F18;
}

/* ── IDE Radio Buttons ────────────────────────────────────────────────── */
QRadioButton {
    color: #C8C8E0;
    spacing: 8px;
    font-size: 13px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #3A3A55;
    background: #0D0D16;
}
QRadioButton::indicator:checked {
    background: #00D4FF;
    border-color: #00D4FF;
}
QRadioButton:hover {
    color: #FFFFFF;
}

/* ── Primary CTA Button ───────────────────────────────────────────────── */
QPushButton#cta_button {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #00B8D9, stop:1 #0055FF);
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #0099DD;
    border-radius: 12px;
    padding: 12px 28px;
    letter-spacing: 0.5px;
}
QPushButton#cta_button:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #11C9EA, stop:1 #2277FF);
    border: 1px solid #11C9EA;
}
QPushButton#cta_button:pressed {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0099BB, stop:1 #0044CC);
}
QPushButton#cta_button:disabled {
    background: #2A2A40;
    color: #5A5A70;
}

/* ── Secondary Buttons ────────────────────────────────────────────────── */
QPushButton#secondary_button {
    background: rgba(255, 255, 255, 0.03);
    color: #A0A0C0;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 10px;
    padding: 9px 20px;
}
QPushButton#secondary_button:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #FFFFFF;
    border-color: rgba(255, 255, 255, 0.2);
}

/* ── Approve Button ───────────────────────────────────────────────────── */
QPushButton#approve_button {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00C896, stop:1 #0066FF);
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
}
QPushButton#approve_button:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00E6AA, stop:1 #3388FF);
}

/* ── Terminal Log Area ────────────────────────────────────────────────── */
QTextEdit#terminal_log {
    background-color: #080810;
    color: #C8E0C8;
    border: 1px solid #1A2A1A;
    border-radius: 8px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 12px;
    selection-background-color: #00D4FF30;
}

/* ── Success Banner ───────────────────────────────────────────────────── */
QWidget#success_banner {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #0D2818, stop:1 #0A1830);
    border: 1px solid #00C896;
    border-radius: 12px;
}

QLabel#success_icon {
    color: #00C896;
    font-size: 42px;
}

QLabel#success_title {
    color: #FFFFFF;
    font-size: 20px;
    font-weight: 700;
}

QLabel#success_sub {
    color: #70A070;
    font-size: 13px;
}

/* ── Spinner Label ────────────────────────────────────────────────────── */
QLabel#spinner_label {
    color: #00D4FF;
    font-size: 13px;
    font-weight: 600;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #7070A0;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover {
    color: #E8E8F0;
}
QTabBar::tab:selected {
    color: #00D4FF;
    border-bottom: 2px solid #00D4FF;
}

/* ── API Key Dialog ───────────────────────────────────────────────────── */
QDialog {
    background-color: #1E1E24;
}
QLineEdit {
    background-color: #0D0D12;
    color: #E8E8F0;
    border: 1px solid #2A2A40;
    border-radius: 6px;
    padding: 8px 10px;
}
QLineEdit:focus {
    border-color: #00D4FF;
}

/* ── Scrollbars ───────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #1A1A24;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #3A3A55;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #00D4FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #1A1A24;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #3A3A55;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #00D4FF;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── IDE Selection Frame & Combo ──────────────────────────────────────── */
QFrame#ide_frame {
    background: #16161E;
    border: 1px solid #2A2A3A;
    border-radius: 10px;
    padding: 4px;
}

QComboBox#ide_combo {
    background: #16161E;
    color: #E8E8F0;
    border: 1px solid #2A2A3A;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 14px;
}
QComboBox#ide_combo:hover {
    border-color: #00D4FF;
    background: #1A1A24;
}
QComboBox#ide_combo::drop-down {
    border: none;
    width: 36px;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
QComboBox#ide_combo::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #00D4FF;
    margin-right: 12px;
}
QComboBox#ide_combo QAbstractItemView {
    background: #1E1E24;
    border: 1px solid #2A2A38;
    border-radius: 8px;
    color: #E8E8F0;
    selection-background-color: transparent;
    outline: none;
}
QComboBox#ide_combo QAbstractItemView::item {
    min-height: 36px;
    padding: 4px 12px;
    border-radius: 6px;
    margin: 4px;
}
QComboBox#ide_combo QAbstractItemView::item:selected {
    background-color: rgba(0, 212, 255, 0.15);
    color: #00D4FF;
}

"""

# ---------------------------------------------------------------------------
# LIGHT THEME
# ---------------------------------------------------------------------------
LIGHT_QSS = """
/* ── Root / Window ────────────────────────────────────────────────────── */
QMainWindow, QWidget#central_widget {
    background-color: #F0F2F8;
}

QWidget {
    font-family: 'Inter', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    color: #1A1A2E;
    background-color: transparent;
}

/* ── Header ───────────────────────────────────────────────────────────── */
QWidget#header_bar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #FFFFFF, stop:1 #F0F4FF);
    border-bottom: 1px solid #D0D8E8;
    min-height: 52px;
    max-height: 52px;
}

QLabel#app_title {
    color: #1A1A2E;
    font-size: 17px;
    font-weight: 700;
    letter-spacing: 1px;
}

/* ── Hamburger Button ─────────────────────────────────────────────────── */
QPushButton#hamburger_btn {
    background: transparent;
    border: none;
    color: #6070A0;
    font-size: 20px;
    padding: 4px 10px;
    border-radius: 6px;
}
QPushButton#hamburger_btn:hover {
    background: rgba(0, 102, 255, 0.08);
    color: #0066FF;
}
QPushButton#hamburger_btn:pressed {
    background: rgba(0, 102, 255, 0.15);
}

/* ── Side Drawer ──────────────────────────────────────────────────────── */
QWidget#side_drawer {
    background: #FFFFFF;
    border-left: 1px solid #D0D8E8;
}

QLabel#drawer_title {
    color: #0066FF;
    font-size: 14px;
    font-weight: 600;
}

QCheckBox#dark_mode_toggle {
    color: #3A3A5E;
    font-size: 13px;
    spacing: 10px;
}
QCheckBox#dark_mode_toggle::indicator {
    width: 40px;
    height: 22px;
    border-radius: 11px;
    background-color: #D0D8E8;
    border: 1px solid #B0BACE;
}
QCheckBox#dark_mode_toggle::indicator:checked {
    background-color: #0066FF;
    border-color: #0066FF;
}

/* ── Panel Cards ──────────────────────────────────────────────────────── */
QWidget#card_panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
}

/* ── Labels ───────────────────────────────────────────────────────────── */
QLabel#section_label {
    color: #0066FF;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
}

QLabel#hero_label {
    color: #1A1A2E;
    font-size: 22px;
    font-weight: 700;
}

QLabel#sub_label {
    color: #8090B0;
    font-size: 13px;
}

/* ── Text Inputs ──────────────────────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #F8F9FC;
    color: #1A1A2E;
    border: 1px solid #D0D8E8;
    border-radius: 8px;
    padding: 10px;
    selection-background-color: #0066FF30;
}
QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #0066FF;
    background-color: #FFFFFF;
}

/* ── IDE Radio Buttons ────────────────────────────────────────────────── */
QRadioButton {
    color: #3A3A5E;
    spacing: 8px;
}
QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border-radius: 8px;
    border: 2px solid #B0BACE;
    background: #FFFFFF;
}
QRadioButton::indicator:checked {
    background: #0066FF;
    border-color: #0066FF;
}
QRadioButton:hover {
    color: #1A1A2E;
}

/* ── Primary CTA Button ───────────────────────────────────────────────── */
QPushButton#cta_button {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #0066FF, stop:1 #0099DD);
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 600;
    border: 1px solid #0055DD;
    border-radius: 12px;
    padding: 12px 28px;
}
QPushButton#cta_button:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:1,
        stop:0 #1177FF, stop:1 #11AAEE);
    border: 1px solid #1177FF;
}
QPushButton#cta_button:pressed {
    background: #0044BB;
}
QPushButton#cta_button:disabled {
    background: #D0D8E8;
    color: #9099B0;
}

/* ── Secondary Buttons ────────────────────────────────────────────────── */
QPushButton#secondary_button {
    background: #F8F9FC;
    color: #4A5568;
    font-size: 13px;
    font-weight: 600;
    border: 1px solid #D0D8E8;
    border-radius: 10px;
    padding: 9px 20px;
}
QPushButton#secondary_button:hover {
    background: #FFFFFF;
    color: #1A202C;
    border-color: #B0BACE;
}

/* ── Approve Button ───────────────────────────────────────────────────── */
QPushButton#approve_button {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00A878, stop:1 #0066FF);
    color: #FFFFFF;
    font-size: 14px;
    font-weight: 700;
    border: none;
    border-radius: 10px;
    padding: 12px 28px;
}
QPushButton#approve_button:hover {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #00C896, stop:1 #3388FF);
}

/* ── Terminal Log Area ────────────────────────────────────────────────── */
QTextEdit#terminal_log {
    background-color: #1A1A28;
    color: #B8D4B8;
    border: 1px solid #3A4060;
    border-radius: 8px;
    font-family: 'Cascadia Code', 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    padding: 12px;
}

/* ── Success Banner ───────────────────────────────────────────────────── */
QWidget#success_banner {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
        stop:0 #E8F8F0, stop:1 #EAF0FF);
    border: 1px solid #00C896;
    border-radius: 12px;
}

QLabel#success_icon {
    color: #00A878;
    font-size: 42px;
}

QLabel#success_title {
    color: #1A2E1A;
    font-size: 20px;
    font-weight: 700;
}

QLabel#success_sub {
    color: #508050;
    font-size: 13px;
}

/* ── Spinner ──────────────────────────────────────────────────────────── */
QLabel#spinner_label {
    color: #0066FF;
    font-size: 13px;
    font-weight: 600;
}

/* ── Tabs ─────────────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: none;
    background: transparent;
}
QTabBar::tab {
    background: transparent;
    color: #8090B0;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}
QTabBar::tab:hover {
    color: #1A1A2E;
}
QTabBar::tab:selected {
    color: #0066FF;
    border-bottom: 2px solid #0066FF;
}

/* ── Dialog ───────────────────────────────────────────────────────────── */
QDialog {
    background-color: #FFFFFF;
}
QLineEdit {
    background-color: #F8F9FC;
    color: #1A1A2E;
    border: 1px solid #D0D8E8;
    border-radius: 6px;
    padding: 8px 10px;
}
QLineEdit:focus {
    border-color: #0066FF;
}

/* ── Scrollbars ───────────────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #EEF2F8;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #B0BACE;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #0066FF;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #EEF2F8;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background: #B0BACE;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background: #0066FF;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── IDE Frame & Combo ────────────────────────────────────────────────── */
QFrame#ide_frame {
    background: #F0F4FF;
    border: 1px solid #D0D8F0;
    border-radius: 10px;
    padding: 4px;
}

QComboBox#ide_combo {
    background: #F8F9FC;
    color: #1A1A2E;
    border: 1px solid #D0D8E8;
    border-radius: 10px;
    padding: 10px 16px;
    font-size: 14px;
}
QComboBox#ide_combo:hover {
    border-color: #0066FF;
    background: #FFFFFF;
}
QComboBox#ide_combo::drop-down {
    border: none;
    width: 36px;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
QComboBox#ide_combo::down-arrow {
    image: none;
    width: 0px;
    height: 0px;
    border-left: 6px solid transparent;
    border-right: 6px solid transparent;
    border-top: 6px solid #0066FF;
    margin-right: 12px;
}
QComboBox#ide_combo QAbstractItemView {
    background: #FFFFFF;
    border: 1px solid #D0D8E8;
    border-radius: 8px;
    color: #1A1A2E;
    selection-background-color: transparent;
    outline: none;
}
QComboBox#ide_combo QAbstractItemView::item {
    min-height: 36px;
    padding: 4px 12px;
    border-radius: 6px;
    margin: 4px;
}
QComboBox#ide_combo QAbstractItemView::item:selected {
    background-color: rgba(0, 102, 255, 0.1);
    color: #0066FF;
}
"""


def get_qss(dark: bool) -> str:
    return DARK_QSS if dark else LIGHT_QSS
