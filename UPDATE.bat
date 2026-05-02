@echo off
chcp 65001 >nul
title Marketingkolabs - Updater
color 1f

echo ===============================================
echo   Marketingkolabs - Auto Updater
echo ===============================================
echo.

:: Check for git
where git >nul 2>&1
if errorlevel 1 (
    echo Git not found. Downloading portable git...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe' -OutFile '%~dp0PortableGit.exe'"
    echo Please run PortableGit.exe and extract to: %~dp0git
    echo Then re-run this script.
    pause
    exit /b 1
)

:: Update main repository (if using git)
if exist ".git" (
    echo Checking for updates...
    git fetch origin
    git status -uno | find "Your branch is behind" >nul
    if not errorlevel 1 (
        echo New version available! Updating...
        git pull origin main
        echo.
        echo Dependencies updated.
    ) else (
        echo Already up to date!
    )
) else (
    echo Not a git repository. Skipping code update.
)

echo.
echo ===============================================
echo   Updating Ollama Model
echo ===============================================
ollama pull phi3:mini

echo.
echo ===============================================
echo   Updating Python packages
echo ===============================================
set "PATH=%~dp0python;%~dp0python\Scripts;%PATH%"
python -m pip install --user -r requirements_free.txt --upgrade

echo.
echo ===============================================
echo   Update Complete!
echo ===============================================
echo.
pause
