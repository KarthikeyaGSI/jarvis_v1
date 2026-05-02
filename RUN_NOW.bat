@echo off
chcp 65001 >nul
title Marketingkolabs - One-Click Start

echo ===============================================
echo   Marketingkolabs - Starting in 3 seconds...
echo ===============================================
timeout /t 3 /nobreak >nul

:: Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo Starting Ollama...
    start /min "" "%~dp0ollama\ollama.exe" serve
    timeout /t 5 /nobreak >nul
)

:: Pull model if needed
"%~dp0ollama\ollama.exe" ls 2>nul | find "phi3:mini" >nul
if errorlevel 1 (
    echo Downloading Phi-3 Mini model (first time only, ~2GB)...
    "%~dp0ollama\ollama.exe" pull phi3:mini
)

:: Start the agent
echo Starting Marketingkolabs Agent...
cd /d "%~dp0"
"%python\python.exe" autonomous_agent.py

pause
