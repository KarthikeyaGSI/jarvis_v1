@echo off
chcp 65001 >nul
title Marketingkolabs - Complete AI Agent

echo ===============================================
echo   Marketingkolabs - Starting Complete System
echo   24/7 Autonomous Agent + All Features
echo ===============================================
echo.

:: Step 1: Check Python
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please run portable\1. Download Portable Tools.bat first
    pause
    exit /b 1
)

:: Step 2: Check Ollama
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Starting Ollama...
    if exist "ollama\ollama.exe" (
        start /min "" "%~dp0ollama\ollama.exe" serve
    ) else (
        ollama serve
    )
    timeout /t 5 /nobreak >nul
)

:: Step 3: Pull model if needed
echo Checking Phi-3 Mini model...
ollama list 2>nul | find "phi3:mini" >nul
if errorlevel 1 (
    echo Downloading Phi-3 Mini (first time only, ~2GB)...
    ollama pull phi3:mini
)

:: Step 4: Install/Update packages
echo Checking Python packages...
python -m pip install --user requests pyperclip pillow 2>nul

:: Step 5: Start the agent
echo.
echo ===============================================
echo   Starting Marketingkolabs Autonomous Agent
echo ===============================================
echo.
echo Features enabled:
echo   ✅ 24/7 Operation
echo   ✅ Crash Recovery
echo   ✅ Multi-Language (EN/HI/TE)
echo   ✅ Gamification System
echo   ✅ Daily Brief & Evening Wrap-up
echo   ✅ Screen Reader (if pyautogui installed)
echo   ✅ Quick Actions
echo   ✅ Auto-Update
echo.
python autonomous_agent.py

pause
