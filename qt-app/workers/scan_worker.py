"""
Auto-ENV — QThread Worker: System Scanner
Runs the full system scan on a background thread to keep the UI responsive.
"""

from __future__ import annotations

import sys
import os

# Ensure engine package is importable when this module is loaded from qt_app
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from PyQt6.QtCore import QObject, QThread, pyqtSignal


class ScanWorker(QObject):
    """Worker that performs the system scan in a background thread."""

    log = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def run(self) -> None:
        try:
            from engine.scanner import scan_system
            self.log.emit("[→] Probing OS & hardware...")
            result = scan_system()
            os_info = result.get("os", {})
            self.log.emit(
                f"[✓] OS: {os_info.get('system','?')} {os_info.get('release','?')} "
                f"({os_info.get('arch','?')})"
            )
            runtimes = result.get("runtimes", {})
            for name, info in runtimes.items():
                ver = info.get("version", "?") if isinstance(info, dict) else info
                mgr = info.get("manager", "") if isinstance(info, dict) else ""
                self.log.emit(f"[✓] Runtime: {name} {ver} {f'({mgr})' if mgr else ''}")
            ports = result.get("ports", {})
            occupied = ports.get("occupied", [])
            suggested = ports.get("suggested_port", 3000)
            if occupied:
                self.log.emit(f"[!] Ports in use: {', '.join(str(p) for p in occupied)}")
            self.log.emit(f"[✓] Suggested free port: {suggested}")
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(f"System scan failed: {exc}")


class ScanThread(QThread):
    """Convenience wrapper that owns the worker and thread lifecycle."""

    log = pyqtSignal(str)
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = ScanWorker()
        self._worker.moveToThread(self)
        self._worker.log.connect(self.log)
        self._worker.finished.connect(self.finished)
        self._worker.error.connect(self.error)
        self.started.connect(self._worker.run)
