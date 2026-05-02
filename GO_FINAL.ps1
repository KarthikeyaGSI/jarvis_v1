# Marketingkolabs - Final Working Launcher
# Run this in PowerShell: cd to folder, then .\GO_FINAL.ps1

Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "  Marketingkolabs - 24/7 Autonomous AI Agent"
Write-Host "  100% Free | No Admin Needed"
Write-Host "=" * 60
Write-Host ""

# Step 1: Check Python
Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
try {
    $ver = python --version 2>&1
    Write-Host "  OK: $ver" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    Write-Host "  Please run portable\1. Download Portable Tools.bat first" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Step 2: Check/Start Ollama
Write-Host "`n[2/4] Checking Ollama..." -ForegroundColor Yellow
$ollamaRunning = $false
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($resp.StatusCode -eq 200) {
        Write-Host "  OK: Ollama is running!" -ForegroundColor Green
        $ollamaRunning = $true
    }
} catch {
    Write-Host "  Ollama not running. Starting..." -ForegroundColor Yellow
}

if (-not $ollamaRunning) {
    # Try to start Ollama
    $ollamaExe = "ollama\ollama.exe"
    if (-not (Test-Path $ollamaExe)) {
        $ollamaExe = "portable\ollama\ollama.exe"
    }
    if (Test-Path $ollamaExe) {
        Start-Process -WindowStyle Minimized -FilePath $ollamaExe -ArgumentList "serve"
        Start-Sleep -Seconds 5
        Write-Host "  Started Ollama!" -ForegroundColor Green
    } else {
        # Try global ollama
        try {
            Start-Process -WindowStyle Minimized -FilePath "ollama" -ArgumentList "serve"
            Start-Sleep -Seconds 5
            Write-Host "  Started Ollama (global)!" -ForegroundColor Green
        } catch {
            Write-Host "  ERROR: Ollama not found!" -ForegroundColor Red
            Write-Host "  Please install from https://ollama.com" -ForegroundColor Yellow
            Read-Host "Press Enter to exit"
            exit 1
        }
    }
}

# Step 3: Check Phi-3 Mini model
Write-Host "`n[3/4] Checking Phi-3 Mini model..." -ForegroundColor Yellow
try {
    $models = ollama list 2>&1
    if ($models -match "phi3") {
        Write-Host "  OK: Phi-3 Mini ready!" -ForegroundColor Green
    } else {
        Write-Host "  Downloading Phi-3 Mini (~2GB, first time only)..." -ForegroundColor Yellow
        ollama pull phi3:mini
    }
} catch {
    Write-Host "  WARNING: Could not check model" -ForegroundColor Yellow
}

# Step 4: Install packages
Write-Host "`n[4/4] Checking Python packages..." -ForegroundColor Yellow
python -m pip install --user requests pyperclip 2>&1 | Out-Null
Write-Host "  OK: Packages ready!" -ForegroundColor Green

# Start the agent
Write-Host "`n" + ("=" * 60) -ForegroundColor Cyan
Write-Host "  STARTING MARKETINGKOLABS AGENT"
Write-Host "  Features: Crash Recovery, Multi-Language, Gamification" -ForegroundColor White
Write-Host "           Daily Brief, Screen Reader, Quick Actions" -ForegroundColor White
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Run the agent
python START_HERE.py
