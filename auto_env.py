"""
Auto-ENV — Entry Point
Launch this file to start the Auto-ENV desktop application.

Usage:
    python auto_env.py

Requirements:
    pip install PyQt6 google-generativeai psutil jsonschema
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# ── Ensure project root is on PYTHONPATH so all packages resolve ──────────
_HERE = Path(__file__).parent.resolve()
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

# ── High-DPI / Scaling (must happen before QApplication) ─────────────────
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


def main() -> None:
    # Enable high-DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("Auto-ENV")
    app.setOrganizationName("AutoENV")
    app.setApplicationVersion("1.0.0")

    # Set a clean default font
    font = QFont("Segoe UI", 10)
    font.setHintingPreference(QFont.HintingPreference.PreferDefaultHinting)
    app.setFont(font)

    from qt_app.main_window import MainWindow
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
