@echo off
SETLOCAL
:: Change directory to where the batch file is located
CD /D "%~dp0"

:: Look for the 'reflow' folder in the current directory
IF EXIST ".\reflow\python.exe" (
    SET "PY_BIN=.\reflow\python.exe"
) ELSE (
    :: Fallback to system python if no local environment exists
    SET "PY_BIN=python"
)

echo [SYSTEM] Launching Reflow Studio...
"%PY_BIN%" studio_gui_v0.5.py
PAUSE