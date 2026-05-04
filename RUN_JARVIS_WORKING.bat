@echo off
title JARVIS SUPER AGENT - WORKING
cd /d "%~dp0"

echo ============================================================
echo   JARVIS SUPER AGENT - WORKING VERSION
echo ============================================================
echo.
echo  Features:
echo    * AI Brain (Ollama phi3:mini) - ONLINE
echo    * Scheduled Tasks - Reminders, recurring commands
echo    * Voice + Text modes
echo    * Full PC Control (apps, files, system)
echo    * Self-healing (auto-installs packages)
echo.
echo  Commands to try:
echo    Help                    - Show all commands
echo    Remind me in 5 min to check email
echo    Run "Take screenshot" every 10 min
echo    Open Chrome
echo    List scheduled tasks
echo.
echo  Starting JARVIS...
echo ============================================================
echo.

python jarvis_working.py

pause
