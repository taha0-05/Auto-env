"""
Auto-ENV — IDE Launcher
Writes SETUP_INSTRUCTIONS.md and opens the project in Antigravity, Kiro, or Cursor.
Falls back to OS file explorer if the IDE isn't in PATH.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Callable

IS_WINDOWS = platform.system() == "Windows"


# ---------------------------------------------------------------------------
# IDE Command Mappings
# ---------------------------------------------------------------------------

_IDE_COMMANDS: dict[str, list[str]] = {
    "antigravity": ["antigravity", "."],
    "kiro": ["kiro", "."],
    "cursor": ["cursor", "."],
    # Fallbacks / aliases
    "vscode": ["code", "."],
    "code": ["code", "."],
}

# On Windows, try .cmd wrappers for electron-based IDEs
_WIN_ALIASES: dict[str, list[str]] = {
    "cursor": ["cursor.cmd", "."],
    "code": ["code.cmd", "."],
}

def find_ide_executable(cmd_name: str) -> str | None:
    """
    Find the absolute path to an IDE executable.
    Checks PATH first, then common Windows installation directories.
    """
    path = shutil.which(cmd_name) or shutil.which(cmd_name + ".cmd") or shutil.which(cmd_name + ".exe")
    if path:
        return path

    if IS_WINDOWS:
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        prog_files = os.environ.get("PROGRAMFILES", "")
        
        paths_to_check = []
        if cmd_name == "code" or cmd_name == "vscode":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "Microsoft VS Code", "bin", "code.cmd"),
                os.path.join(prog_files, "Microsoft VS Code", "bin", "code.cmd"),
                os.path.join(local_app_data, "Programs", "Microsoft VS Code", "Code.exe"),
                os.path.join(prog_files, "Microsoft VS Code", "Code.exe")
            ]
        elif cmd_name == "cursor":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "cursor", "Cursor.exe"),
                os.path.join(local_app_data, "Programs", "cursor", "resources", "app", "bin", "cursor.cmd")
            ]
        elif cmd_name == "antigravity":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "antigravity", "antigravity.exe"),
                os.path.join(local_app_data, "Programs", "Antigravity IDE", "antigravity.exe"),
                os.path.join(prog_files, "antigravity", "antigravity.exe"),
                os.path.join(prog_files, "Antigravity IDE", "antigravity.exe")
            ]
        elif cmd_name == "kiro":
            paths_to_check = [
                os.path.join(local_app_data, "Programs", "kiro", "kiro.exe"),
                os.path.join(prog_files, "kiro", "kiro.exe")
            ]
            
        for p in paths_to_check:
            if os.path.isfile(p):
                return p

    return None


def discover_installed_ides() -> list[tuple[str, str]]:
    """
    Returns a list of tuples (Label, Command_or_Path) for installed IDEs.
    Detects via Windows Registry and system PATH.
    """
    ides_found = []
    seen_labels = set()
    
    known_ides = [
        ("VS Code", ["visual studio code", "vs code"], ["code", "code.cmd"]),
        ("Cursor", ["cursor"], ["cursor", "cursor.cmd"]),
        ("Antigravity", ["antigravity"], ["antigravity", "antigravity.exe", "Antigravity IDE.exe"]),
        ("Kiro", ["kiro"], ["kiro", "kiro.exe"]),
        ("PyCharm", ["pycharm"], ["pycharm64", "pycharm"]),
        ("IntelliJ IDEA", ["intellij idea"], ["idea64", "idea"]),
        ("WebStorm", ["webstorm"], ["webstorm64", "webstorm"]),
        ("Android Studio", ["android studio"], ["studio64", "studio"]),
        ("Sublime Text", ["sublime text"], ["subl", "sublime_text"]),
        ("Notepad++", ["notepad++"], ["notepad++"]),
        ("Fleet", ["fleet"], ["fleet"]),
        ("Zed", ["zed"], ["zed"]),
        ("Neovim", ["neovim"], ["nvim"]),
        ("Vim", ["vim"], ["vim"]),
        ("Eclipse", ["eclipse"], ["eclipse"]),
        ("Visual Studio", ["visual studio build tools", "visual studio community", "visual studio professional", "visual studio enterprise"], ["devenv"]),
    ]
    
    if IS_WINDOWS:
        import winreg
        keys = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
        ]
        for hive, key in keys:
            try:
                with winreg.OpenKey(hive, key) as reg_key:
                    for i in range(winreg.QueryInfoKey(reg_key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(reg_key, i)
                            with winreg.OpenKey(reg_key, subkey_name) as subkey:
                                try:
                                    name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                except FileNotFoundError:
                                    continue
                                
                                name_lower = name.lower()
                                
                                for label, keywords, _ in known_ides:
                                    if label in seen_labels:
                                        continue
                                    
                                    for kw in keywords:
                                        if kw in name_lower:
                                            try:
                                                display_icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                                if display_icon and display_icon.lower().endswith(".exe"):
                                                    clean_path = display_icon.strip('"')
                                                    if os.path.exists(clean_path):
                                                        ides_found.append((label, clean_path))
                                                        seen_labels.add(label)
                                                        break
                                            except FileNotFoundError:
                                                pass
                                            break
                        except OSError:
                            pass
            except OSError:
                pass

    for label, _, cmds in known_ides:
        if label in seen_labels:
            continue
            
        for cmd in cmds:
            path = find_ide_executable(cmd)
            if path:
                ides_found.append((label, path))
                seen_labels.add(label)
                break
                
    if not ides_found:
        ides_found.append(("Explorer", "explorer"))
        
    return ides_found


def _try_launch(cmd: list[str], cwd: str) -> bool:
    """Try to launch a subprocess. Returns True on success."""
    flags = subprocess.CREATE_NO_WINDOW if IS_WINDOWS else 0
    try:
        subprocess.Popen(
            cmd,
            cwd=cwd,
            creationflags=flags,
            close_fds=True,
        )
        return True
    except FileNotFoundError:
        return False
    except Exception:
        return False


def _open_explorer(path: str) -> None:
    """Open the OS file manager at the given path."""
    try:
        if IS_WINDOWS:
            subprocess.Popen(["explorer", path])
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Setup Instructions Writer
# ---------------------------------------------------------------------------

def write_setup_instructions(
    project_path: str,
    blueprint: dict,
    ide_name: str,
    log_fn: Callable[[str], None] | None = None,
) -> None:
    """Write SETUP_INSTRUCTIONS.md into the project root."""
    stack = blueprint.get("stack", {})
    start_cmd = blueprint.get("start_command", "")
    env_vars = blueprint.get("env_vars", {})
    notes = blueprint.get("notes", "")

    lines = [
        "# Auto-ENV — Setup Instructions",
        "",
        f"**Project:** `{blueprint.get('project_name','')}`  ",
        f"**Language:** {stack.get('language','?')}  ",
        f"**Framework:** {stack.get('framework','?')}  ",
        f"**Runtime:** {stack.get('runtime_version','?')}  ",
        "",
        "## Environment Variables",
        "",
        "These are already written to your `.env` file:",
        "",
    ]
    for k, v in env_vars.items():
        lines.append(f"- `{k}={v}`")

    if start_cmd:
        lines += [
            "",
            "## Start Command",
            "",
            f"```\n{start_cmd}\n```",
        ]

    if notes:
        lines += ["", "## Notes", "", notes]

    lines += [
        "",
        "---",
        f"*Generated by Auto-ENV · IDE: {ide_name}*",
    ]

    dest = Path(project_path) / "SETUP_INSTRUCTIONS.md"
    try:
        dest.write_text("\n".join(lines), encoding="utf-8")
        if log_fn:
            log_fn("[✓] SETUP_INSTRUCTIONS.md written.")
    except OSError as exc:
        if log_fn:
            log_fn(f"[!] Could not write instructions: {exc}")


# ---------------------------------------------------------------------------
# Launch
# ---------------------------------------------------------------------------

def launch_ide(
    ide_name: str,
    project_path: str,
    blueprint: dict,
    log_fn: Callable[[str], None] | None = None,
) -> bool:
    """
    Write setup instructions and open the project in the chosen IDE.
    Returns True if the IDE launched, False if fallback to explorer was used.
    """
    def _log(msg: str):
        if log_fn:
            log_fn(msg)

    write_setup_instructions(project_path, blueprint, ide_name, log_fn)

    key = ide_name.lower().strip()
    
    # Try resolving absolute path first
    abs_path = find_ide_executable(key)
    if abs_path:
        _log(f"[→] Launching {ide_name} ({abs_path}) ...")
        if _try_launch([abs_path, "."], cwd=project_path):
            _log(f"[✓] {ide_name} launched successfully.")
            return True
            
    # Fallback to pure commands if not found by our resolver (maybe linux alias)
    cmds_to_try: list[list[str]] = []
    if key in _IDE_COMMANDS:
        cmds_to_try.append(_IDE_COMMANDS[key])
    if IS_WINDOWS and key in _WIN_ALIASES:
        cmds_to_try.append(_WIN_ALIASES[key])

    for cmd in cmds_to_try:
        _log(f"[→] Launching {ide_name} ({' '.join(cmd)}) ...")
        if _try_launch(cmd, cwd=project_path):
            _log(f"[✓] {ide_name} launched successfully.")
            return True

    _log(f"[!] '{ide_name}' not found in PATH — opening file explorer instead.")
    _open_explorer(project_path)
    return False
