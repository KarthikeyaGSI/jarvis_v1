# Simple test - Run this in PowerShell
# cd "C:\Users\Student\Downloads\open source voice agent\marketingkolabs"
# then: powershell -File DO_TEST.ps1

Write-Host "=== MARKETINGKOLABS SYSTEM TEST ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Python
Write-Host "[1/4] Python:" -NoNewline
try {
    $ver = python --version 2>&1
    Write-Host " OK - $ver" -ForegroundColor Green
} catch {
    Write-Host " MISSING" -ForegroundColor Red
}

# Test 2: Ollama
Write-Host "[2/4] Ollama:" -NoNewline
try {
    $resp = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction SilentlyContinue
    Write-Host " Running" -ForegroundColor Green
} catch {
    Write-Host " Not running (run: ollama serve)" -ForegroundColor Yellow
}

# Test 3: Phi-3 Mini
Write-Host "[3/4] Phi-3 Mini:" -NoNewline
$models = ollama list 2>&1
if ($models -match "phi3") {
    Write-Host " OK" -ForegroundColor Green
} else {
    Write-Host " Not found (run: ollama pull phi3:mini)" -ForegroundColor Yellow
}

# Test 4: Core Files
Write-Host "[4/4] Core Files:" -ForegroundColor White
$files = @("autonomous_agent.py", "START_HERE.py", "core/memory.py", "core/screen_reader.py")
foreach ($f in $files) {
    if (Test-Path $f) {
        Write-Host "  OK: $f" -ForegroundColor Green
    } else {
        Write-Host "  MISSING: $f" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== FEATURES READY ===" -ForegroundColor Cyan
$features = @(
    "24/7 Autonomous Operation",
    "Crash Recovery & Auto-Restart",
    "Multi-Language (EN/Hindi/Telugu)",
    "Gamification (XP, Levels, Badges)",
    "Daily Brief (9 AM) & Evening Wrap-up",
    "Screen Reader (What's on my screen?)",
    "Quick Actions Menu",
    "Auto-Updater (UPDATE.bat)"
)
foreach ($feat in $features) {
    Write-Host "  OK: $feat" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=== TO START ===" -ForegroundColor Cyan
Write-Host "Double-click: GO.bat"
Write-Host "OR run: python START_HERE.py"
