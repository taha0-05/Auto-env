@echo off
title Auto-ENV
echo Starting Auto-ENV...

rem Use the virtual environment Python
"%~dp0.venv\Scripts\python.exe" "%~dp0auto_env.py"

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Auto-ENV failed to start. See message above.
    pause
)
