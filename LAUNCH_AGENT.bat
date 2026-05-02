@echo off
chcp 65001 >nul
title Marketingkolabs - 24/7 Autonomous AI Agent

echo ==============================================
echo   Marketingkolabs - Starting System
echo   24/7 Autonomous Operation + All Features
echo ==============================================
echo.

:: Check if Ollama is running
echo [1/4] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Ollama not running. Starting...
    if exist "ollama\ollama.exe" (
        start /min "" "ollama\ollama.exe" serve
    ) else (
        if exist "portable\ollama\ollama.exe" (
            start /min "" "portable\ollama\ollama.exe" serve
        ) else (
            ollama serve
        )
    )
    timeout /t 5 /nobreak >nul
)

:: Check Phi-3 Mini model
echo [2/4] Checking Phi-3 Mini model...
ollama list 2>nul | find "phi3:mini" >nul
if errorlevel 1 (
    echo Downloading Phi-3 Mini (first time only, ~2GB)...
    ollama pull phi3:mini
)

:: Check Python packages
echo [3/4] Checking Python packages...
python -m pip install --user requests pyperclip pillow 2>nul

:: Start the agent
echo [4/4] Starting Marketingkolabs Autonomous Agent...
echo.
echo ==============================================
echo   Features Enabled:
echo     [OK] 24/7 Operation with Crash Recovery
echo     [OK] Multi-Language (EN/Hindi/Telugu)
echo     [OK] Gamification System (XP, Levels, Badges)
echo     [OK] Smart Daily Brief (9 AM) & Evening Wrap-up (6 PM)
echo     [OK] Screen Reader (if pyautogui installed)
echo     [OK] Quick Actions Menu
echo     [OK] Auto-Updater (run UPDATE.bat)
echo     [OK] 100%% Free | No Admin Needed
echo ==============================================
echo.

python START_HERE.py

pause
