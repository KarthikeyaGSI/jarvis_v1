"""
Marketingkolabs - Main Runner
This script checks everything and starts the agent with voice
"""
import os
import sys
import time
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_24-7.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('RUN_NOW')

def check_python():
    """Check Python version"""
    print("[1/5] Checking Python...")
    print(f"  Python: {sys.version.split(chr(10))[0]}")
    print("  OK!")
    return True

def check_ollama():
    """Check if Ollama is running"""
    print("\n[2/5] Checking Ollama...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.ok:
            print("  OK: Ollama is running!")
            return True
        else:
            print("  WARNING: Ollama not responding")
            return False
    except:
        print("  WARNING: Ollama not running")
        return False

def start_ollama():
    """Try to start Ollama"""
    print("\n  Attempting to start Ollama...")
    try:
        ollama_exe = "ollama\\ollama.exe" if os.path.exists("ollama\\ollama.exe") else (
            "portable\\ollama\\ollama.exe" if os.path.exists("portable\\ollama\\ollama.exe") else "ollama"
        )
        import subprocess
        subprocess.Popen([ollama_exe, "serve"], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        time.sleep(5)
        print("  Started Ollama!")
        return True
    except Exception as e:
        print(f"  Failed: {e}")
        return False

def check_model():
    """Check Phi-3 Mini model"""
    print("\n[3/5] Checking Phi-3 Mini model...")
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], 
                               capture_output=True, text=True, timeout=10)
        if "phi3" in result.stdout.lower():
            print("  OK: Phi-3 Mini ready!")
            return True
        else:
            print("  Model not found. Pulling Phi-3 Mini (~2GB)...")
            subprocess.run(["ollama", "pull", "phi3:mini"], timeout=300)
            print("  OK: Model downloaded!")
            return True
    except Exception as e:
        print(f"  WARNING: {e}")
        return False

def check_packages():
    """Check Python packages"""
    print("\n[4/5] Checking Python packages...")
    packages = ['requests', 'sqlite3', 'json', 'threading']
    for pkg in packages:
        try:
            __import__(pkg)
            print(f"  OK: {pkg}")
        except:
            print(f"  WARNING: {pkg} (may need install)")
    return True

def start_agent():
    """Start the autonomous agent"""
    print("\n[5/5] Starting Marketingkolabs Autonomous Agent...")
    print("\n" + "="*60)
    print("  MARKETINGKOLABS - 24/7 AUTONOMOUS AGENT")
    print("="*60 + "\n")
    print("Features:")
    print("  [OK] 24/7 Operation with Crash Recovery")
    print("  [OK] Multi-Language (English/Hindi/Telugu)")
    print("  [OK] Gamification System (XP, Levels, Badges)")
    print("  [OK] Smart Daily Brief (9 AM) & Evening Wrap-up (6 PM)")
    print("  [OK] Screen Reader (if pyautogui installed)")
    print("  [OK] Quick Actions Menu")
    print("  [OK] Auto-Updater (run UPDATE.bat)")
    print("  [OK] Voice will speak responses!")
    print("\n" + "="*60)
    print("  Type 'exit' to stop. Type anything to interact.")
    print("  Try: 'What time is it?' or 'Search for Python'")
    print("="*60 + "\n")

    try:
        from autonomous_agent import AutonomousAgent
        agent = AutonomousAgent()
        agent.start()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nERROR: {e}")
        print("Check agent_24-7.log for details.")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("  MARKETINGKOLABS - SYSTEM CHECK")
    print("="*60 + "\n")

    check_python()

    if not check_ollama():
        start_ollama()
        check_ollama()

    check_model()
    check_packages()
    start_agent()
