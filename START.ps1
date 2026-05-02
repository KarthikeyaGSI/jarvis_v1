# Marketingkolabs - Start Complete System
# Run this in PowerShell

Write-Host "=" * 60
Write-Host "  Marketingkolabs - 24/7 Autonomous AI Agent"
Write-Host "  100% Free | No Admin | All Features Enabled"
Write-Host "=" * 60
Write-Host ""

# Step 1: Check Ollama
Write-Host "[1/4] Checking Ollama..."
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2
    Write-Host "✓ Ollama is running!" -ForegroundColor Green
} catch {
    Write-Host "⚠ Ollama not running. Starting..." -ForegroundColor Yellow
    if (Test-Path "ollama\ollama.exe") {
        Start-Process -WindowStyle Minimized "ollama\ollama.exe" "serve"
    } elseif (Test-Path "portable\ollama\ollama.exe") {
        Start-Process -WindowStyle Minimized "portable\ollama\ollama.exe" "serve"
    } else {
        ollama serve
    }
    Start-Sleep -Seconds 5
}

# Step 2: Check Model
Write-Host "`n[2/4] Checking Phi-3 Mini model..."
$models = ollama list 2>&1
if ($models -match "phi3:mini") {
    Write-Host "✓ Phi-3 Mini model ready!" -ForegroundColor Green
} else {
    Write-Host "Downloading Phi-3 Mini (first time only, ~2GB)..." -ForegroundColor Yellow
    ollama pull phi3:mini
}

# Step 3: Install Python packages
Write-Host "`n[3/4] Checking Python packages..."
pip install --user requests pyperclip pillow 2>&1 | Out-Null
Write-Host "✓ Python packages ready!" -ForegroundColor Green

# Step 4: Start Agent
Write-Host "`n[4/4] Starting Marketingkolabs Autonomous Agent..."
Write-Host ""
Write-Host "=" * 60
Write-Host "  Features: Crash Recovery, Multi-Language, Gamification"
Write-Host "           Daily Brief, Screen Reader, Quick Actions"
Write-Host "=" * 60
Write-Host ""

python START_HERE.py
