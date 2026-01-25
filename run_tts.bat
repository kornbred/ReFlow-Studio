@echo off
title ReFlow Studio - Launcher

:: --- 1. THE MAGIC LINE ---
:: This tells Python: "Ignore C:\Users\...\AppData\Roaming\Python" completely.
set PYTHONNOUSERSITE=1

:: --- 2. ACTIVATE ENVIRONMENT ---
:: We use call to make sure the script continues after activation
call conda activate reflow

:: --- 3. RUN TTS HANDLER ---
echo [LAUNCHER] 🚀 Running TTS Handler in Strict Mode...
echo [LAUNCHER] 🙈 Ignoring C: Drive User Packages...
echo.

python "core/tts/tts_handler.py"

echo.
echo [LAUNCHER] ✅ Execution Finished.
pause