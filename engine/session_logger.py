"""
Auto-ENV — Session Logger
Appends structured JSON log entries to scan.log in the user's home config dir.
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path


_LOG_DIR = Path.home() / ".autoenv"
_LOG_FILE = _LOG_DIR / "scan.log"


def _ensure_log_dir() -> None:
    _LOG_DIR.mkdir(parents=True, exist_ok=True)


def append_session(
    *,
    prompt: str,
    stack: dict,
    assigned_port: int | None,
    project_path: str,
    success: bool,
    duration_seconds: float,
    error_message: str = "",
) -> None:
    """Append one session record to scan.log."""
    _ensure_log_dir()
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt_preview": prompt[:120],
        "stack": stack,
        "assigned_port": assigned_port,
        "project_path": project_path,
        "success": success,
        "duration_seconds": round(duration_seconds, 2),
        "error_message": error_message,
    }
    try:
        with _LOG_FILE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
    except OSError as exc:
        # Log to stderr but never crash the app
        import sys
        print(f"[session_logger] WARNING: Could not write to {_LOG_FILE}: {exc}", file=sys.stderr)


def get_log_path() -> str:
    return str(_LOG_FILE)
