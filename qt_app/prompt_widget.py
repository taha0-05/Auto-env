import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTextEdit
from PyQt6.QtCore import pyqtSignal

class PromptWidget(QWidget):
    """Widget displayed at application start.
    Emits ``analyzeRequested`` with the raw prompt text when the user clicks *Analyze*.
    """
    analyzeRequested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zero‑Setup Project Builder")
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Describe the project you want to build (e.g., \"Create a Python Flask web app on port 5000\" )"))
        self.inputEdit = QLineEdit(self)
        layout.addWidget(self.inputEdit)

        self.analyzeBtn = QPushButton("Analyze & Prepare", self)
        layout.addWidget(self.analyzeBtn)
        self.analyzeBtn.clicked.connect(self._on_analyze)

        self.logView = QTextEdit(self)
        self.logView.setReadOnly(True)
        layout.addWidget(self.logView)

    def _on_analyze(self):
        prompt = self.inputEdit.text().strip()
        if prompt:
            self.logView.append(f"🗒️ Prompt received: {prompt}")
            self.analyzeRequested.emit(prompt)
        else:
            self.logView.append("⚠️ Please enter a description before analyzing.")
