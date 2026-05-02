@echo off
title JARVIS Premium UI
cd /d "%~dp0"
echo ============================================================
echo   JARVIS Premium UI - Starting...
echo ============================================================
echo.
echo [1/2] Starting JARVIS Server...
echo [2/2] Opening Premium UI in browser...
echo.
echo JARVIS UI: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

start "" http://localhost:5000

python jarvis_server.py

pause
