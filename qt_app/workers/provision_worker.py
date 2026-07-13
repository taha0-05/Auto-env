"""
Auto-ENV — QThread Worker: Provisioner
Runs project provisioning (directory creation, venv/npm, pip/npm install, .env write)
on a background thread with real-time log streaming.
"""

from __future__ import annotations

import sys
import os
import time

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class ProvisionWorker(QObject):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)   # success, project_path
    error = pyqtSignal(str)

    def __init__(self, blueprint: dict, base_path: str):
        super().__init__()
        self._blueprint = blueprint
        self._base_path = base_path
        self._cancelled = False

    def cancel(self) -> None:
        self._cancelled = True

    def _stop_flag(self) -> bool:
        return self._cancelled

    def run(self) -> None:
        start = time.monotonic()
        try:
            from engine.provisioner import provision
            project_path = provision(
                blueprint=self._blueprint,
                base_path=self._base_path,
                log_fn=self.log.emit,
                stop_flag=self._stop_flag,
            )
            duration = time.monotonic() - start
            self.log.emit(f"[✓] Done in {duration:.1f}s")
            self.finished.emit(True, project_path)
        except InterruptedError:
            self.log.emit("[!] Provisioning cancelled.")
            self.finished.emit(False, "")
        except Exception as exc:
            self.log.emit(f"[✗] Provisioning error: {exc}")
            self.error.emit(str(exc))
            self.finished.emit(False, "")


class ProvisionThread(QThread):
    log = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    error = pyqtSignal(str)

    def __init__(self, blueprint: dict, base_path: str, parent=None):
        super().__init__(parent)
        self._worker = ProvisionWorker(blueprint, base_path)
        self._worker.moveToThread(self)
        self._worker.log.connect(self.log)
        self._worker.finished.connect(self.finished)
        self._worker.error.connect(self.error)
        self.started.connect(self._worker.run)

    def cancel(self) -> None:
        self._worker.cancel()
