"""
Auto-ENV — Provisioner
Creates isolated project workspaces, installs dependencies, writes .env files.
Handles Windows vs Unix binary naming, permission errors, and collision suffixes.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable, Optional


IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _run_live(
    cmd: list[str],
    cwd: str,
    log_fn: Callable[[str], None],
    env: dict | None = None,
) -> int:
    """Run a subprocess and stream its stdout/stderr to log_fn line-by-line."""
    flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    try:
        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=merged_env,
            creationflags=flags,
        )
        for line in proc.stdout:  # type: ignore[union-attr]
            stripped = line.rstrip()
            if stripped:
                log_fn(f"    {stripped}")
        proc.wait()
        return proc.returncode
    except FileNotFoundError as exc:
        log_fn(f"[✗] Command not found: {cmd[0]} — {exc}")
        return -1
    except Exception as exc:
        log_fn(f"[✗] Subprocess error: {exc}")
        return -1


def _npm_bin() -> str:
    """Return 'npm.cmd' on Windows, 'npm' elsewhere."""
    return "npm.cmd" if IS_WINDOWS else "npm"


def _pip_bin(venv_path: str) -> str:
    """Return the pip binary inside a venv."""
    if IS_WINDOWS:
        return str(Path(venv_path) / "Scripts" / "pip.exe")
    return str(Path(venv_path) / "bin" / "pip")


def _python_bin(venv_path: str) -> str:
    if IS_WINDOWS:
        return str(Path(venv_path) / "Scripts" / "python.exe")
    return str(Path(venv_path) / "bin" / "python")


# ---------------------------------------------------------------------------
# Directory Creation
# ---------------------------------------------------------------------------

def create_project_dir(base_path: str, project_name: str) -> str:
    """
    Create a project directory at base_path/project_name.
    If the directory already exists, append _1, _2, … until a free slot is found.
    Returns the actual path created.
    """
    base = Path(base_path)
    candidate = base / project_name
    counter = 1
    while candidate.exists():
        candidate = base / f"{project_name}_{counter}"
        counter += 1

    try:
        candidate.mkdir(parents=True, exist_ok=False)
        return str(candidate)
    except PermissionError as exc:
        raise PermissionError(
            f"Cannot create project directory '{candidate}': {exc}\n"
            "Try choosing a different base path or running as administrator."
        )


# ---------------------------------------------------------------------------
# Environment Setup
# ---------------------------------------------------------------------------

def setup_python_venv(project_path: str, log_fn: Callable[[str], None]) -> str:
    """Create a Python venv at project_path/.venv. Returns venv path."""
    venv = str(Path(project_path) / ".venv")
    log_fn(f"[→] Creating Python virtual environment at .venv ...")
    rc = _run_live([sys.executable, "-m", "venv", venv], cwd=project_path, log_fn=log_fn)
    if rc != 0:
        raise RuntimeError(f"venv creation failed (exit code {rc})")
    log_fn("[✓] Virtual environment created.")
    return venv


def setup_node_project(project_path: str, log_fn: Callable[[str], None]) -> None:
    """Initialise a Node project with npm init -y."""
    log_fn("[→] Initialising Node.js project (npm init) ...")
    rc = _run_live([_npm_bin(), "init", "-y"], cwd=project_path, log_fn=log_fn)
    if rc != 0:
        log_fn(f"[!] npm init returned code {rc} — continuing anyway.")
    else:
        log_fn("[✓] Node project initialised.")


def install_python_deps(
    venv_path: str,
    project_path: str,
    dependencies: list[str],
    log_fn: Callable[[str], None],
) -> None:
    """Install Python packages using pip inside the venv."""
    if not dependencies:
        log_fn("[→] No Python dependencies to install.")
        return
    pip = _pip_bin(venv_path)
    # Fallback: if venv pip doesn't exist, use sys pip
    if not Path(pip).exists():
        pip = "pip"
    log_fn(f"[→] Installing {len(dependencies)} Python package(s): {', '.join(dependencies)}")
    rc = _run_live([pip, "install", "--upgrade", "pip"], cwd=project_path, log_fn=log_fn)
    rc = _run_live([pip, "install"] + dependencies, cwd=project_path, log_fn=log_fn)
    if rc == 0:
        log_fn("[✓] Python dependencies installed.")
    else:
        log_fn(f"[!] pip install returned code {rc}. Check your internet connection.")


def install_node_deps(
    project_path: str,
    dependencies: list[str],
    log_fn: Callable[[str], None],
) -> None:
    """Install Node packages using npm install."""
    if not dependencies:
        log_fn("[→] No Node dependencies to install.")
        return
    log_fn(f"[→] Installing {len(dependencies)} Node package(s) ...")
    rc = _run_live([_npm_bin(), "install"] + dependencies, cwd=project_path, log_fn=log_fn)
    if rc == 0:
        log_fn("[✓] Node dependencies installed.")
    else:
        log_fn(f"[!] npm install returned code {rc}.")


# ---------------------------------------------------------------------------
# .env Writer
# ---------------------------------------------------------------------------

def write_env_file(project_path: str, env_vars: dict, log_fn: Callable[[str], None]) -> None:
    """Write a .env file to the project root."""
    env_path = Path(project_path) / ".env"
    lines = [f"{k}={v}" for k, v in env_vars.items()]
    try:
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        log_fn(f"[✓] .env file written ({len(lines)} variable(s)).")
    except OSError as exc:
        log_fn(f"[✗] Could not write .env: {exc}")


# ---------------------------------------------------------------------------
# Directory Structure Creation
# ---------------------------------------------------------------------------

def create_structure(project_path: str, structure: list[str], log_fn: Callable[[str], None]) -> None:
    """Create the directory/file skeleton from the blueprint's structure list."""
    root = Path(project_path)
    for item in structure:
        target = root / item
        try:
            if item.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                if not target.exists():
                    target.write_text("", encoding="utf-8")
        except OSError as exc:
            log_fn(f"[!] Could not create {item}: {exc}")
    log_fn(f"[✓] Project structure created ({len(structure)} item(s)).")


# ---------------------------------------------------------------------------
# Main Provision Orchestrator
# ---------------------------------------------------------------------------

def provision(
    blueprint: dict,
    base_path: str,
    log_fn: Callable[[str], None],
    stop_flag: Callable[[], bool] | None = None,
) -> str:
    """
    Full provisioning pipeline. Returns the created project path.
    stop_flag: callable that returns True if the worker has been cancelled.
    """
    def _check_stop():
        if stop_flag and stop_flag():
            raise InterruptedError("Provisioning cancelled by user.")

    project_name = blueprint.get("project_name", "my_project")
    stack = blueprint.get("stack", {})
    language = stack.get("language", "python").lower()
    dependencies = blueprint.get("dependencies", [])
    env_vars = blueprint.get("env_vars", {})
    structure = blueprint.get("structure", [])

    log_fn(f"[→] Creating project directory: {project_name}")
    project_path = create_project_dir(base_path, project_name)
    log_fn(f"[✓] Project root: {project_path}")

    _check_stop()

    # Create directory skeleton
    if structure:
        create_structure(project_path, structure, log_fn)

    _check_stop()

    # Language-specific setup
    venv_path: str | None = None
    if language == "python":
        try:
            venv_path = setup_python_venv(project_path, log_fn)
        except RuntimeError as exc:
            log_fn(f"[!] venv setup failed: {exc} — trying global pip.")
        _check_stop()
        install_python_deps(venv_path or "", project_path, dependencies, log_fn)

    elif language in ("node", "javascript", "typescript"):
        setup_node_project(project_path, log_fn)
        _check_stop()
        install_node_deps(project_path, dependencies, log_fn)

    else:
        log_fn(f"[→] Stack '{language}' — skipping automated dependency install.")

    _check_stop()

    # Write .env
    write_env_file(project_path, env_vars, log_fn)

    log_fn(f"[✓] Provisioning complete → {project_path}")
    return project_path
