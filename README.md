# Auto-ENV

**Intelligent Dev Environment Provisioner**

Auto-ENV is a PyQt6 desktop app that turns a natural-language project request into a provisioned local development workspace.

## Why this exists

Setting up a new project often means repeating the same manual steps: checking runtimes, picking a free port, creating folders, initializing environments, installing dependencies, writing `.env`, and opening an IDE. Auto-ENV automates that flow while keeping a human approval step before provisioning.

## End-to-end workflow

1. Enter a project request in natural language and choose an IDE.
2. Auto-ENV scans your system (OS, runtimes, and common dev ports).
3. Gemini generates a JSON blueprint.
4. The blueprint is validated against schema rules and shown for review.
5. You approve the plan.
6. Auto-ENV provisions the project:
   - creates the project directory,
   - creates a Python `.venv` or initializes a Node project,
   - installs dependencies,
   - writes `.env`,
   - writes `SETUP_INSTRUCTIONS.md`.
7. Auto-ENV launches the selected IDE (or falls back to file explorer).

## Features

- Natural-language project intent input
- System scanning (OS/runtimes/ports)
- Gemini-powered blueprint generation with JSON schema validation
- Explicit user approval before provisioning
- Automated Python/Node project setup and dependency installation
- `.env` and `SETUP_INSTRUCTIONS.md` generation
- IDE discovery/launch with explorer fallback
- Session logging to `~/.autoenv/scan.log`

## Prerequisites

- Python 3 (recommended: 3.10+)
- Internet access for Gemini API and package installation
- Gemini API key
- On Windows, optional use of the included batch launcher

Install dependencies from `requirements.txt`:

- `PyQt6>=6.6.0`
- `google-generativeai>=0.8.0`
- `psutil>=5.9.0`
- `jsonschema>=4.21.0`

## Installation

From the repository root:

```bash
python -m venv .venv
```

### Windows

```bat
.venv\Scripts\pip install -r requirements.txt
run_auto_env.bat
```

Or directly:

```bat
.venv\Scripts\python.exe auto_env.py
```

### Generic Python environment (Linux/macOS/other)

```bash
source .venv/bin/activate
pip install -r requirements.txt
python auto_env.py
```

## API key setup

Auto-ENV looks for your Gemini key in this order:

1. `GEMINI_API_KEY` environment variable
2. `~/.autoenv/gemini_key.txt`

### Option A: environment variable

```bash
export GEMINI_API_KEY="your_key_here"
```

(Windows PowerShell)

```powershell
$env:GEMINI_API_KEY="your_key_here"
```

### Option B: app-managed key file

If no env var is found, the app prompts for the key and saves it to:

```text
~/.autoenv/gemini_key.txt
```

## Project output

By default, generated projects are created under:

```text
~/AutoENV-Projects
```

Typical generated output includes:

- project root folder (with collision suffixes like `_1`, `_2` if needed)
- Python `.venv` (for Python stacks) or `npm init` output (for Node stacks)
- installed dependencies
- `.env`
- `SETUP_INSTRUCTIONS.md`

## High-level architecture / layout

```text
auto_env.py                      # Main entry point
run_auto_env.bat                 # Windows launcher
requirements.txt                 # Python dependencies

engine/
  scanner.py                     # OS/runtime/port scanning
  gemini_client.py               # Gemini call + JSON extraction/validation
  provisioner.py                 # Project creation, venv/npm, deps, .env
  ide_launcher.py                # IDE discovery/launch + setup instructions
  nlp.py                         # Lightweight/demo prompt parsing
  resolver.py                    # Lightweight/demo action resolution
  graph.py                       # Lightweight/demo graph packaging
  session_logger.py              # Session log append/read path helpers

qt_app/
  main_window.py                 # Main multi-step PyQt workflow coordinator
  workers/                       # Scan/Gemini/provision background workers
  widgets/                       # Input/blueprint/progress/completion UI
  approval_dialog.py             # Approval dialog components
  graph_view.py                  # Graph display components

find_ides.py                     # Standalone IDE discovery helper script
test_discover.py                 # IDE discovery test script
test_combo.py                    # PyQt combo/icon experiment script
```

## Supported stacks and behavior

- Runtime detection includes Python, Node/npm, Cargo, and Go.
- Blueprint schema can represent multiple languages/frameworks.
- Provisioning is currently primarily automated for:
  - **Python** (creates `.venv`, installs pip dependencies)
  - **Node/JavaScript/TypeScript** (`npm init -y`, installs npm dependencies)
- Other stack languages are not fully auto-provisioned in `engine/provisioner.py` and are currently treated as limited/skip-install paths.

IDE discovery includes:

- VS Code, Cursor, Antigravity, Kiro, PyCharm, IntelliJ IDEA, WebStorm,
  Android Studio, Sublime Text, Notepad++, Fleet, Zed, Neovim, Vim,
  Eclipse, and Visual Studio
- Explorer/file-manager fallback when preferred IDE is unavailable

## Development and testing notes

This repository currently contains lightweight/manual test scripts rather than a full automated test suite:

- `test_discover.py`: prints discovered IDEs using the discovery logic
- `test_combo.py`: small PyQt combo/icon rendering experiment

Run scripts directly from the repo root (example):

```bash
python test_discover.py
python test_combo.py
```

Notes:

- `test_discover.py` is mainly useful on Windows where registry-based IDE discovery is implemented.
- `test_combo.py` requires a GUI-capable environment with PyQt6.

## Security notes

- Gemini API keys are loaded from `GEMINI_API_KEY` or `~/.autoenv/gemini_key.txt`.
- Generated project `.env` files may contain sensitive values from blueprint output; review and rotate values as needed.
- Provisioning is not automatic until you review and approve the generated blueprint in the UI.

## Troubleshooting

### Missing Gemini API key

- Set `GEMINI_API_KEY`, or
- Launch app and provide key when prompted (saved to `~/.autoenv/gemini_key.txt`).

### Preferred IDE not found

If selected IDE is not found, Auto-ENV opens the generated project in file explorer as fallback.

### Dependency installation failures

Common causes:

- no internet connection,
- unavailable package version,
- missing runtime tooling in `PATH` (`pip`, `npm`),
- environment permission issues.

Re-run after fixing runtime/network issues.

### Windows-specific behavior

- `run_auto_env.bat` expects Python at `.venv\Scripts\python.exe`.
- IDE discovery on Windows also checks common install paths and registry uninstall entries.
- Some subprocesses use Windows-specific flags to avoid opening extra console windows.

## Limitations / known status

- The repository contains both the main PyQt workflow and some lightweight/demo modules (`engine/nlp.py`, `engine/resolver.py`, `engine/graph.py`, helper scripts).
- Provisioning automation is currently focused on Python and Node-oriented flows.
