@echo off
title JARVIS SUPER-PREMIUM v2.0
cd /d "%~dp0"

echo ============================================================
echo   JARVIS SUPER-PREMIUM v2.0 - AI POWERED
echo ============================================================
echo.
echo  Features:
echo   * AI Brain (Ollama phi3:mini)
echo   * Self-Healing (auto-installs packages)
echo   * Particle Effects UI
echo   * Voice + Text modes
echo   * Full PC Control
echo.
echo  Starting server...
echo ============================================================
echo.

start "" http://localhost:5000
python jarvis_server.py

pause
