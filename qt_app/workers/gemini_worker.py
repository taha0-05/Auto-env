"""
Auto-ENV — QThread Worker: Gemini API
Calls the Gemini API on a background thread, emitting log and blueprint signals.
"""

from __future__ import annotations

import sys
import os

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class GeminiWorker(QObject):
    """Worker that calls Gemini and emits a validated blueprint dict."""

    log = pyqtSignal(str)
    finished = pyqtSignal(dict)   # blueprint
    error = pyqtSignal(str)

    def __init__(self, prompt: str, system_info: dict, api_key: str = ""):
        super().__init__()
        self._prompt = prompt
        self._system_info = system_info
        self._api_key = api_key

    def run(self) -> None:
        try:
            from engine.gemini_client import generate_blueprint, GeminiError
            blueprint = generate_blueprint(
                self._prompt,
                self._system_info,
                api_key=self._api_key or None,
                log_fn=self.log.emit,
            )
            self.finished.emit(blueprint)
        except Exception as exc:
            self.error.emit(str(exc))


class GeminiThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, prompt: str, system_info: dict, api_key: str = "", parent=None):
        super().__init__(parent)
        self._worker = GeminiWorker(prompt, system_info, api_key)
        self._worker.moveToThread(self)
        self._worker.log.connect(self.log)
        self._worker.finished.connect(self.finished)
        self._worker.error.connect(self.error)
        self.started.connect(self._worker.run)
