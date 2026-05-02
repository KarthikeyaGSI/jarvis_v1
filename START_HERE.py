"""
Marketingkolabs - START HERE
The main entry point for the 24/7 autonomous voice agent
Voice-controlled PC access - just speak and it executes!
"""
import os
import sys
import time
import logging
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_24-7.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.ok:
            logger.info("Ollama is running")
            return True
        else:
            logger.warning("Ollama not responding properly")
            return False
    except:
        logger.error("Ollama is not running!")
        logger.error("Please start it: ollama serve")
        return False


def check_model():
    """Check if Phi-3 Mini model is available"""
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=10)
        if "phi3" in result.stdout.lower():
            logger.info("Phi-3 Mini model ready")
            return True
        else:
            logger.warning("Phi-3 Mini not found. Pulling...")
            subprocess.run(["ollama", "pull", "phi3:mini"], timeout=300)
            return True
    except Exception as e:
        logger.error(f"Could not check model: {e}")
        return False


def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 60)
    print("  MARKETINGKOLABS - VOICE-CONTROLLED PC AGENT")
    print("  100% Free | No Admin | No Credit Card")
    print("=" * 60)
    print()
    print("Features:")
    print("  [OK] Voice Control - Speak to control your PC")
    print("  [OK] Wake Word Mode - Say 'Hey Google' to activate")
    print("  [OK] Hotkey Mode - Press Ctrl+Shift+Space")
    print("  [OK] Open apps, search web, control system")
    print("  [OK] Multi-Language (English/Hindi/Telugu)")
    print("  [OK] Gamification System (XP, Levels, Badges)")
    print("  [OK] Smart Daily Brief (9 AM) & Evening Wrap-up")
    print("  [OK] Screen Reader (What's on my screen?)")
    print()
    print("Voice Commands You Can Use:")
    print("  - 'What time is it?'")
    print("  - 'Open Chrome' / 'Open browser'")
    print("  - 'Search for Python tutorials'")
    print("  - 'daily brief' / 'evening wrapup'")
    print("  - 'gamification status'")
    print("  - 'switch personality jarvis'")
    print()
    print("=" * 60)
    print("  Voice mode: Say commands to control your PC")
    print("=" * 60 + "\n")


def main():
    """Main entry point - launches voice-controlled agent"""
    print_banner()

    # Check system
    if not check_ollama():
        print("\nWARNING: Please start Ollama first:")
        print("  1. Open a new terminal")
        print("  2. Run: ollama serve")
        print("  3. In another terminal, run: python START_HERE.py\n")
        sys.exit(1)

    check_model()

    # Import and start voice-controlled agent
    try:
        from autonomous_agent import AutonomousAgent
        logger.info("All modules loaded successfully")

        agent = AutonomousAgent()
        agent.start()

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        logger.info("Agent stopped by user")
    except Exception as e:
        logger.critical(f"CRITICAL ERROR: {e}")
        print(f"\nError: {e}")
        print("Check agent_24-7.log for details")
        input("Press Enter to exit...")


if __name__ == "__main__":
    import sys
    if '--hotkey' in sys.argv:
        # Run with hotkey mode (Ctrl+Shift+Space by default)
        hotkey = 'ctrl+shift+space'
        if '--win-space' in sys.argv:
            print("Note: Win+Space may require admin rights on Windows")
            hotkey = 'win+space'
        agent = AutonomousAgent()
        agent.start(mode='hotkey')
    elif '--web' in sys.argv:
        # Run web UI
        from api_server import start_server
        start_server()
    else:
        # Default: voice mode (continuous listening)
        main()
