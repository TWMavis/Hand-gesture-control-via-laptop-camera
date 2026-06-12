@echo off
rem HandControl launcher: double-click to run (ESC to quit, SPACE to pause)
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] .venv not found. Install first - see README.md:
    echo   uv venv --python 3.12 .venv
    echo   uv pip install -r requirements.txt --python .venv
    pause
    exit /b 1
)

rem stderr goes to a log file to hide MediaPipe internal noise;
rem real errors are printed below when the app exits abnormally
".venv\Scripts\python.exe" main.py 2>"last_run_stderr.log"

if errorlevel 1 (
    echo.
    echo [ERROR] HandControl exited abnormally:
    type "last_run_stderr.log"
    pause
)
