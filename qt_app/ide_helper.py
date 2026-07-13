import subprocess
import os
import sys

def open_ide(project_path: str) -> None:
    """Open the given project in VS Code or fallback to Explorer."""
    # Ensure the path is absolute
    project_path = os.path.abspath(project_path)
    try:
        # Try VS Code if available in PATH
        subprocess.Popen(["code", project_path])
    except FileNotFoundError:
        # Fallback: open Windows Explorer at the project folder
        subprocess.Popen(["explorer", project_path])
    except Exception as e:
        print(f"Failed to open IDE: {e}", file=sys.stderr)
