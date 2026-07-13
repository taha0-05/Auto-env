"""
Auto-ENV — System Scanner (rewritten)
Performs OS/hardware detection, runtime probing, and socket-level port scanning.
"""

from __future__ import annotations

import platform
import socket
import subprocess
import sys
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run(cmd: list[str]) -> Optional[str]:
    """Run a shell command and return stripped stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=8,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        out = result.stdout.strip()
        return out if out else None
    except Exception:
        return None


def _run_shell(cmd: str) -> Optional[str]:
    """Run a shell command string (shell=True) for PATH-sensitive lookups."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=8,
            shell=True,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
        )
        out = result.stdout.strip()
        return out if out else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# OS & Hardware
# ---------------------------------------------------------------------------

def detect_os() -> dict:
    machine = platform.machine().lower()
    arch = "arm64" if "arm" in machine or "aarch" in machine else "x64"
    return {
        "system": platform.system(),          # Windows / Darwin / Linux
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "arch": arch,
        "python_executable": sys.executable,
    }


# ---------------------------------------------------------------------------
# Runtime Detection
# ---------------------------------------------------------------------------

def _detect_python() -> dict:
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    manager = "global"

    # Check pyenv
    pyenv_root = _run_shell("pyenv root") or ""
    if pyenv_root and Path(pyenv_root).exists():
        manager = "pyenv"

    # Check virtualenv / venv
    if sys.prefix != sys.base_prefix:
        manager = "virtualenv"

    return {"version": version, "manager": manager, "executable": sys.executable}


def _detect_node() -> Optional[dict]:
    # Try nvm-managed node first
    nvm_dir = Path.home() / ".nvm"
    if nvm_dir.exists():
        ver = _run_shell("node -v")
        if ver:
            return {"version": ver.lstrip("v"), "manager": "nvm"}

    # Try global node
    ver = _run(["node", "--version"]) or _run(["node.exe", "--version"])
    if ver:
        return {"version": ver.lstrip("v"), "manager": "global"}

    return None


def _detect_npm() -> Optional[str]:
    ver = _run(["npm", "--version"]) or _run(["npm.cmd", "--version"])
    return ver


def detect_runtimes() -> dict:
    runtimes: dict = {}
    runtimes["python"] = _detect_python()

    node = _detect_node()
    if node:
        runtimes["node"] = node
        npm = _detect_npm()
        if npm:
            runtimes["npm"] = {"version": npm}

    # Cargo / Rust
    cargo = _run(["cargo", "--version"])
    if cargo:
        parts = cargo.split()
        runtimes["cargo"] = {"version": parts[1] if len(parts) > 1 else cargo}

    # Go
    go = _run(["go", "version"])
    if go:
        runtimes["go"] = {"version": go.split()[2].lstrip("go") if len(go.split()) > 2 else go}

    return runtimes


# ---------------------------------------------------------------------------
# Socket-Level Port Scanner
# ---------------------------------------------------------------------------

_DEV_PORTS = [3000, 3001, 4000, 4200, 5000, 5001, 5173, 8000, 8080, 8888, 9000]
_EPHEMERAL_START = 49200
_EPHEMERAL_END = 65000


def _is_port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """Return True if the port is occupied (refuses bind)."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.settimeout(0.3)
            s.bind((host, port))
            return False  # Bind succeeded → port is free
    except OSError:
        return True  # Could not bind → port is occupied


def scan_ports() -> dict:
    """
    Scan common dev ports and return:
      - occupied: list of occupied ports
      - free_dev: list of free dev ports
      - suggested_port: first free dev port, or ephemeral fallback
    """
    occupied = [p for p in _DEV_PORTS if _is_port_in_use(p)]
    free_dev = [p for p in _DEV_PORTS if p not in occupied]

    if free_dev:
        suggested = free_dev[0]
    else:
        # All common dev ports occupied — pick from ephemeral range
        suggested = _EPHEMERAL_START
        while suggested < _EPHEMERAL_END:
            if not _is_port_in_use(suggested):
                break
            suggested += 1

    return {
        "occupied": occupied,
        "free_dev": free_dev,
        "suggested_port": suggested,
    }


def resolve_port(preferred: int) -> int:
    """Return `preferred` if free, else find the next free port."""
    if not _is_port_in_use(preferred):
        return preferred
    # Try adjacent ports first
    for p in range(preferred + 1, preferred + 50):
        if not _is_port_in_use(p):
            return p
    # Fallback to ephemeral range
    p = _EPHEMERAL_START
    while p < _EPHEMERAL_END:
        if not _is_port_in_use(p):
            return p
        p += 1
    return preferred  # Last resort: return original


# ---------------------------------------------------------------------------
# Full Scan
# ---------------------------------------------------------------------------

def scan_system() -> dict:
    os_info = detect_os()
    runtimes = detect_runtimes()
    ports = scan_ports()
    return {
        "os": os_info,
        "runtimes": runtimes,
        "ports": ports,
    }
