@echo off
title JARVIS Super Agent
cd /d "%~dp0"
echo ============================================================
echo   JARVIS SUPER AGENT - Full PC Control
echo ============================================================
echo.
echo  * Lock screen, sleep, shutdown, restart
echo  * Open any app, file, or folder
echo  * Control volume, screenshots, clipboard
echo  * Type text, click mouse, press keys
echo  * System info, battery, CPU, RAM
echo.
echo Type commands or say 'voice' for voice mode
echo ============================================================
echo.

python super_agent.py

pause
