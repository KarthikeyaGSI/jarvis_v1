@echo off
chcp 65001 >nul
title Marketingkolabs - Autonomous AI Agent

echo ==============================================
echo   Marketingkolabs - 24/7 Autonomous AI
echo   100%% Free | No Admin | No Credit Card
echo ==============================================
echo.

:: Check if Ollama is running
echo [1/3] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Ollama not running. Starting...
    if exist "ollama\ollama.exe" (
        start /min "" "ollama\ollama.exe" serve
    ) else (
        ollama serve
    )
    timeout /t 5 /nobreak >nul
)

:: Pull model if needed
echo [2/3] Checking Phi-3 Mini model...
ollama list 2>nul | find "phi3:mini" >nul
if errorlevel 1 (
    echo Downloading Phi-3 Mini (first time only, ~2GB)...
    ollama pull phi3:mini
)

:: Start the agent
echo [3/3] Starting Marketingkolabs Autonomous Agent...
echo.
echo Features: Crash Recovery, Multi-Language, Gamification
echo          Daily Brief, Screen Reader, Quick Actions
echo.
python START_HERE.py

pause
