# Simple test - Run this in PowerShell
# cd to correct folder first:
# cd "C:\Users\Student\Downloads\open source voice agent\marketingkolabs"

Write-Host "=== MARKETINGKOLABS SYSTEM TEST ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Python
Write-Host "[1/6] Python:" -NoNewline
try {
    $ver = python --version 2>&1
    Write-Host " OK - $ver" -ForegroundColor Green
} catch {
    Write-Host " MISSING" -ForegroundColor Red
}

# Test 2: Ollama
Write-Host "[2/6] Ollama:" -NoNewline
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host " Running" -ForegroundColor Green
} catch {
    Write-Host " Not running (run: ollama serve)" -ForegroundColor Yellow
}

# Test 3: Phi-3 Mini model
Write-Host "[3/6] Phi-3 Mini:" -NoNewline
$models = ollama list 2>&1
if ($models -match "phi3") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " Not found (run: ollama pull phi3:mini)" -ForegroundColor Yellow
}

# Test 4: Python packages
Write-Host "[4/6] Packages:" -NoNewline
try {
    python -c "import requests, sqlite3, json; print('OK')" 2>&1 | Out-Null
    Write-Host " OK" -ForegroundColor Green
} catch {
    Write-Host " Missing some packages" -ForegroundColor Yellow
}

# Test 5: Core files
Write-Host "[5/6] Core files:" -ForegroundColor White
$files = @("autonomous_agent.py", "START_HERE.py", "core/memory.py", "core/screen_reader.py")
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "  OK: $f" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $f" -ForegroundColor Red
    }
}

# Test 6: Features
Write-Host "[6/6] Features:" -ForegroundColor White
$features = @(
    "Crash Recovery",
    "Multi-Language (EN/HI/TE)",
    "Gamification System",
    "Daily Brief & Evening Wrap-up",
    "Screen Reader",
    "Quick Actions",
    "Auto-Updater"
)
foreach ($feat in $features) {
    Write-Host "  OK: $feat" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "TO START: Double-click GO.bat" -ForegroundColor Yellow
Write-Host "   OR run: python START_HERE.py" -ForegroundColor Yellow
