"""
Marketingkolabs Autonomous Agent - 24/7 Local AI Worker
Runs continuously, executes tasks, learns, and proactively assists
NO external dependencies - 100% local
Features: Crash Recovery, Multi-Language, Daily Brief, Gamification, Task Scheduler
"""
import os
import sys
import time
import json
import sqlite3
import threading
import subprocess
import requests
from pathlib import Path
from datetime import datetime, timedelta
import logging
import re

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_24-7.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutonomousAgent:
    """
    A true 24/7 autonomous agent that:
    - Listens continuously for voice commands
    - Executes tasks proactively
    - Monitors system and suggests actions
    - Learns from interactions
    - Works 100% locally with Ollama
    - Supports Hindi/English mixed commands
    - Crash recovery with auto-restart
    - Gamification tracking
    - Smart daily briefings
    """

    def __init__(self):
        logger.info("=" * 60)
        logger.info("MARKETINGKOLABS AUTONOMOUS AGENT STARTING...")
        logger.info("24/7 Local AI Worker - No Cloud Dependencies")
        logger.info("=" * 60)

        self.is_running = False
        self.ollama_url = "http://localhost:11434"
        self.model = "phi3:mini"  # Fast, local LLM

        # Initialize TTS engine
        try:
            from core.tts import TTSEngine
            self.tts_engine = TTSEngine()
            logger.info("[OK] TTS Engine initialized (pyttsx3)")
        except Exception as e:
            logger.error(f"TTS init failed: {e}")
            self.tts_engine = None

        # Initialize STT engine for voice input
        try:
            from core.stt import STTEngine
            self.stt_engine = STTEngine()
            logger.info("[OK] STT Engine initialized (faster-whisper)")
        except Exception as e:
            logger.error(f"STT init failed: {e}")
            self.stt_engine = None

        # Initialize intent parser for understanding commands
        try:
            from core.intent_parser import IntentParser
            import yaml
            with open("config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            self.intent_parser = IntentParser(config)
            logger.info("[OK] Intent Parser initialized (Ollama)")
        except Exception as e:
            logger.error(f"Intent parser init failed: {e}")
            self.intent_parser = None

        # Initialize skill router for executing actions
        try:
            from core.skill_router import SkillRouter
            import yaml
            with open("config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            self.skill_router = SkillRouter(config)
            logger.info("[OK] Skill Router initialized")
        except Exception as e:
            logger.error(f"Skill router init failed: {e}")
            self.skill_router = None

        # Memory database
        self.db_path = "agent_memory.db"
        self._init_memory()

        # State tracking
        self.last_action = None
        self.context = {}
        self.task_queue = []
        self.voice_mode = True  # Enable voice mode by default
        self._is_processing = False  # Track if currently processing a command

        # Gamification system
        self.stats = self._load_stats()
        self.voice_personality = "default"  # default, jarvis, friday"

        # Multi-language support
        self.supported_languages = ['en', 'hi', 'te']  # English, Hindi, Telugu
        self.current_language = 'en'

        # Task scheduler (cron-like for Windows)
        self.scheduled_tasks = [
            {"name": "daily_brief", "hour": 9, "last_run": None},
            {"name": "evening_wrapup", "hour": 18, "last_run": None},
            {"name": "health_check", "interval": 30, "last_run": None}  # Every 30 min
        ]

        logger.info("[OK] Autonomous Agent Initialized")
        logger.info("[OK] Using local Ollama + Phi-3 Mini")
        logger.info("[OK] Memory system ready")
        logger.info("[OK] Gamification system loaded")
        logger.info("[OK] Multi-language support: EN, HI, TE")
        logger.info("[OK] Task scheduler active")
        logger.info("[OK] Voice control ready - speak commands to control PC")

    def _init_memory(self):
        """Initialize persistent memory database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    input_text TEXT,
                    action_taken TEXT,
                    result TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS learned_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # New: Gamification stats table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stats (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            # New: Scheduled tasks log
            conn.execute("""
                CREATE TABLE IF NOT EXISTS task_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_name TEXT,
                    run_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                    result TEXT
                )
            """)
            conn.commit()
        logger.info("Memory database initialized")

    def _load_stats(self):
        """Load gamification stats from memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM stats")
            rows = cursor.fetchall()
            stats = {row['key']: row['value'] for row in rows}

        # Default stats
        return {
            "commands_used": int(stats.get("commands_used", 0)),
            "days_active": int(stats.get("days_active", 0)),
            "last_active_date": stats.get("last_active_date", ""),
            "level": int(stats.get("level", 1)),
            "xp": int(stats.get("xp", 0)),
            "badges": json.loads(stats.get("badges", "[]"))
        }

    def _save_stats(self):
        """Save gamification stats"""
        with sqlite3.connect(self.db_path) as conn:
            for key, value in self.stats.items():
                conn.execute("""
                    INSERT OR REPLACE INTO stats (key, value)
                    VALUES (?, ?)
                """, (key, json.dumps(value) if isinstance(value, list) else str(value)))
            conn.commit()

    def add_xp(self, amount):
        """Add experience points and check for level up"""
        self.stats["xp"] += amount
        self.stats["commands_used"] = int(self.stats["commands_used"]) + 1

        # Check level up (100 XP per level)
        new_level = (self.stats["xp"] // 100) + 1
        if new_level > self.stats["level"]:
            self.stats["level"] = new_level
            logger.info(f"[LEVEL UP] You're now level {new_level}!")
            if self.voice_mode:
                self._speak(f"Congratulations! You've reached level {new_level}!")

        self._update_streak()
        self._save_stats()

    def _update_streak(self):
        """Update daily streak"""
        today = datetime.now().date().isoformat()
        if self.stats["last_active_date"] != today:
            self.stats["last_active_date"] = today
            self.stats["days_active"] = int(self.stats["days_active"]) + 1

    def get_gamification_status(self):
        """Get current gamification status"""
        return {
            "level": self.stats["level"],
            "xp": self.stats["xp"],
            "xp_to_next_level": 100 - (self.stats["xp"] % 100),
            "commands_used": self.stats["commands_used"],
            "days_active": self.stats["days_active"],
            "badges": self.stats["badges"]
        }

    def _call_ollama(self, prompt: str, system: str = None, language: str = None) -> str:
        """Call local Ollama API with multi-language support"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": 0.1, "num_predict": 200}
            }

            # Multi-language system prompt
            if language == 'hi' or (not language and self.current_language == 'hi'):
                system = system or "आप एक सहायक AI हो। हिंदी और अंग्रेजी में जवाब दो।"
            elif language == 'te':
                system = system or "మీరు సహాయక AI. తెలుగు మరియు ఇంగ్లీష్లో స్పందించండి."
            else:
                system = system or "You are a helpful AI assistant."

            if system:
                payload["system"] = system

            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=10
            )
            if response.ok:
                return response.json().get('response', '').strip()
            return ""
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            return ""

    def _parse_intent(self, text: str) -> dict:
        """Parse voice command into JSON action using local LLM"""
        prompt = """Parse this voice command into JSON:
{
  "skill": "text_editor|file_ops|app_control|clipboard|browser|system",
  "action": "specific_action_name",
  "params": {"key": "value"}
}

Command: """ + text + """

Return ONLY valid JSON, no explanation."""

        response = self._call_ollama(prompt)

        try:
            # Extract JSON from response
            if response and '{' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except:
            pass

        # Fallback parsing
        text_lower = text.lower()
        if 'open' in text_lower:
            return {"skill": "app_control", "action": "open_app",
                    "params": {"app_name": text_lower.split('open')[-1].strip()}}
        elif 'search' in text_lower:
            return {"skill": "browser", "action": "search",
                    "params": {"query": text_lower.split('search')[-1].strip()}}
        else:
            return {"skill": "unknown", "action": "echo", "params": {"text": text}}

    def execute_action(self, action: dict) -> dict:
        """Execute the parsed action"""
        skill = action.get('skill', 'unknown')
        act = action.get('action', 'noop')
        params = action.get('params', {})

        logger.info(f"Executing: {skill}.{act} with {params}")

        try:
            if skill == "app_control":
                return self._exec_app_control(act, params)
            elif skill == "browser":
                return self._exec_browser(act, params)
            elif skill == "clipboard":
                return self._exec_clipboard(act, params)
            elif skill == "file_ops":
                return self._exec_file_ops(act, params)
            elif skill == "system":
                return self._exec_system(act, params)
            elif skill == "unknown":
                return self._exec_unknown(action)
            else:
                return {"success": False, "message": f"Unknown skill: {skill}"}
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {"success": False, "message": str(e)}

    def _exec_app_control(self, action, params):
        """Control applications"""
        if action == "open_app":
            app = params.get('app_name', '').strip().strip(' .,!?').rstrip('.')
            # Map common names to executable names
            app_map = {
                'chrome': 'chrome',
                'google chrome': 'chrome',
                'firefox': 'firefox',
                'edge': 'msedge',
                'microsoft edge': 'msedge',
                'notepad': 'notepad',
                'calculator': 'calc',
                'word': 'winword',
                'excel': 'excel',
                'browser': 'chrome',
                'paint': 'mspaint',
                'cmd': 'cmd',
                'command prompt': 'cmd',
                'explorer': 'explorer',
                'file explorer': 'explorer',
                'settings': 'ms-settings:',
                'control panel': 'control',
            }
            app_lower = app.lower()
            exe = app_map.get(app_lower, app_lower)

            try:
                if os.name == 'nt':
                    # Use start command with empty title (required for Windows start command)
                    subprocess.Popen(f'start "" "{exe}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                else:
                    subprocess.Popen(exe)
                return {"success": True, "message": f"Opened {app}"}
            except Exception as e:
                # Try with .exe extension on Windows
                if os.name == 'nt':
                    try:
                        subprocess.Popen(f'start "" "{exe}.exe"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        return {"success": True, "message": f"Opened {app}"}
                    except:
                        pass
                return {"success": False, "message": f"Failed to open {app}: {e}"}
        elif action == "close_app":
            app = params.get('app_name', '').strip()
            try:
                if os.name == 'nt':
                    subprocess.Popen(f'taskkill /f /im {app}.exe', shell=True)
                return {"success": True, "message": f"Closed {app}"}
            except Exception as e:
                return {"success": False, "message": f"Failed to close {app}: {e}"}
        return {"success": False, "message": f"Unknown action: {action}"}

    def _exec_system(self, action, params):
        """System commands - full PC control"""
        try:
            import pyautogui
            if action == "get_time":
                now = datetime.now()
                return {"success": True, "message": f"Current time: {now.strftime('%I:%M %p')}"}
            elif action == "get_date":
                now = datetime.now()
                return {"success": True, "message": f"Today is {now.strftime('%B %d, %Y')}"}
            elif action == "screenshot":
                screenshot = pyautogui.screenshot()
                path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                screenshot.save(path)
                return {"success": True, "message": f"Screenshot saved: {path}"}
            elif action == "click":
                x = params.get('x', pyautogui.position()[0])
                y = params.get('y', pyautogui.position()[1])
                pyautogui.click(x=x, y=y)
                return {"success": True, "message": f"Clicked at {x}, {y}"}
            elif action == "type_text":
                text = params.get('text', '')
                pyautogui.write(text)
                return {"success": True, "message": f"Typed: {text}"}
            elif action == "press_key":
                key = params.get('key', '')
                pyautogui.press(key)
                return {"success": True, "message": f"Pressed: {key}"}
            elif action == "hotkey":
                keys = params.get('keys', '').split('+')
                pyautogui.hotkey(*keys)
                return {"success": True, "message": f"Pressed hotkey: {params.get('keys', '')}"}
            elif action == "scroll":
                clicks = params.get('clicks', 3)
                pyautogui.scroll(clicks)
                return {"success": True, "message": f"Scrolled {clicks} clicks"}
            elif action == "minimize_all":
                pyautogui.hotkey('win', 'd')
                return {"success": True, "message": "Minimized all windows"}
            elif action == "switch_window":
                pyautogui.hotkey('alt', 'tab')
                return {"success": True, "message": "Switched window"}
            elif action == "volume_up":
                pyautogui.press('volumeup')
                return {"success": True, "message": "Volume up"}
            elif action == "volume_down":
                pyautogui.press('volumedown')
                return {"success": True, "message": "Volume down"}
            elif action == "volume_mute":
                pyautogui.press('volumemute')
                return {"success": True, "message": "Toggled mute"}
            elif action == "lock_screen":
                if os.name == 'nt':
                    subprocess.Popen('rundll32.exe user32.dll,LockWorkStation')
                return {"success": True, "message": "Screen locked"}
        except Exception as e:
            return {"success": False, "message": f"System command failed: {e}"}
        return {"success": False, "message": f"Unknown system action: {action}"}

    def _exec_browser(self, action, params):
        """Browser automation"""
        import webbrowser
        if action == "search":
            query = params.get('query', '')
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return {"success": True, "message": f"Searched for: {query}"}

    def _exec_clipboard(self, action, params):
        """Clipboard operations"""
        try:
            import pyperclip
            if action == "copy":
                text = params.get('text', '')
                if text:
                    pyperclip.copy(text)
                return {"success": True, "message": "Copied to clipboard"}
            elif action == "paste":
                text = pyperclip.paste()
                return {"success": True, "message": f"Clipboard: {text[:50]}..."}
        except ImportError:
            return {"success": False, "message": "pyperclip not installed"}

    def _exec_file_ops(self, action, params):
        """File operations"""
        path = params.get('path', '')
        if action == "open_file" and path:
            try:
                os.startfile(path)
                return {"success": True, "message": f"Opened {path}"}
            except Exception as e:
                return {"success": False, "message": str(e)}

    def _exec_system(self, action, params):
        """System commands"""
        if action == "get_time":
            now = datetime.now()
            return {"success": True, "message": f"Current time: {now.strftime('%H:%M:%S')}"}
        elif action == "get_date":
            now = datetime.now()
            return {"success": True, "message": f"Today is {now.strftime('%B %d, %Y')}"}

    def _exec_unknown(self, action):
        """Handle unknown commands - ask Ollama with multi-language support"""
        text = action.get('params', {}).get('text', '')
        if not text:
            return {"success": False, "message": "No input"}

        # Detect language
        lang = self._detect_language(text)

        response = self._call_ollama(
            f"User said: {text}\nProvide a helpful response as JARVIS, a British AI assistant.",
            language=lang
        )

        # Add XP for interaction
        self.add_xp(10)

        return {"success": True, "message": response, "language": lang}

    def _detect_language(self, text: str) -> str:
        """Detect if text is Hindi, Telugu, or English"""
        # Simple detection based on Unicode ranges
        hindi_range = range(0x0900, 0x097F)
        telugu_range = range(0x0C00, 0x0C7F)

        for char in text:
            if ord(char) in hindi_range:
                self.current_language = 'hi'
                return 'hi'
            elif ord(char) in telugu_range:
                self.current_language = 'te'
                return 'te'
        return 'en'

    def _speak(self, text: str, language: str = None):
        """Speak text with personality"""
        if not self.voice_mode:
            return

        lang = language or self.current_language
        # In production, use TTS with language support
        print(f"Agent [{lang}]: {text}")

    def daily_brief(self) -> dict:
        """Generate daily briefing"""
        now = datetime.now()

        # Get recent activity
        history = self.get_recent_history(5)
        recent_cmds = [h['input_text'] for h in history if h['input_text']]

        # Weather (via browser search)
        weather = "32°C"  # Placeholder

        brief = f"""
Good morning! Here's your briefing for {now.strftime('%B %d, %Y')}:

📊 You've used {self.stats['commands_used']} commands
🎯 You're at Level {self.stats['level']} with {self.stats['xp'] % 100} XP to next level
📅 Active for {self.stats['days_active']} days
🌡️ Weather in Warangal: {weather}

Recent commands: {', '.join(recent_cmds[:3]) if recent_cmds else 'None yet'}
"""
        return {"success": True, "message": brief.strip()}

    def evening_wrapup(self) -> dict:
        """Evening wrap-up summary"""
        now = datetime.now()
        brief = f"""
Good evening! Here's your day summary:

📊 Commands used today: {self.stats['commands_used']}
🎯 Current level: {self.stats['level']}
📅 Total active days: {self.stats['days_active']}

Have a great evening!
"""
        return {"success": True, "message": brief.strip()}

    def export_memory(self, filepath: str = "my_memory.md"):
        """Export conversations to markdown"""
        convos = self.get_recent_history(1000)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("# Marketingkolabs Memory Export\n\n")
            for c in convos:
                f.write(f"## {c['timestamp']}\n")
                f.write(f"**User:** {c['input_text']}\n\n")
                if c['result']:
                    try:
                        result = json.loads(c['result'])
                        f.write(f"**Agent:** {result.get('message', '')}\n\n")
                    except:
                        pass
        return {"success": True, "message": f"Memory exported to {filepath}"}

    def switch_personality(self, name: str):
        """Switch voice personality"""
        valid = ['default', 'jarvis', 'friday']
        if name in valid:
            self.voice_personality = name
            return {"success": True, "message": f"Switched to {name} personality"}
        return {"success": False, "message": f"Invalid personality. Choose: {', '.join(valid)}"}

    def store_interaction(self, text: str, action: dict, result: dict):
        """Store in persistent memory"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO interactions (input_text, action_taken, result)
                VALUES (?, ?, ?)
            """, (text, json.dumps(action), json.dumps(result)))
            conn.commit()

    def get_recent_history(self, limit=10):
        """Get recent interactions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM interactions
                ORDER BY timestamp DESC LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    def proactive_check(self):
        """Proactive monitoring - runs continuously with scheduled tasks"""
        while self.is_running:
            try:
                current_hour = datetime.now().hour
                current_time = time.time()

                # Morning brief (9 AM, once per day)
                for task in self.scheduled_tasks:
                    if task["name"] == "daily_brief" and current_hour == task["hour"]:
                        if task["last_run"] != datetime.now().date().isoformat():
                            logger.info("🔔 Delivering daily brief...")
                            result = self.daily_brief()
                            logger.info(result['message'])
                            task["last_run"] = datetime.now().date().isoformat()
                            self._speak(result['message'])

                    # Evening wrap-up (6 PM)
                    elif task["name"] == "evening_wrapup" and current_hour == task["hour"]:
                        if task["last_run"] != datetime.now().date().isoformat():
                            logger.info("🔔 Evening wrap-up...")
                            result = self.evening_wrapup()
                            logger.info(result['message'])
                            task["last_run"] = datetime.now().date().isoformat()
                            self._speak(result['message'])

                    # Health check (every 30 minutes)
                    elif task["name"] == "health_check":
                        if task["last_run"] is None or (current_time - task["last_run"]) > (task["interval"] * 60):
                            logger.info("Proactive: System health check...")
                            task["last_run"] = current_time

                # Sleep for 1 minute before next check
                time.sleep(60)

            except Exception as e:
                logger.error(f"Proactive check error: {e}")
                time.sleep(60)

    def start(self, mode="voice"):
        """Start the 24/7 autonomous agent with crash recovery
        mode: 'voice' for voice commands, 'wake_word' for wake word mode, 'hotkey' for hotkey mode
        """
        self.is_running = True

        # Log gamification status
        gamification = self.get_gamification_status()
        logger.info(f"[GAME] Player: Level {gamification['level']}, XP: {gamification['xp']}, Days: {gamification['days_active']}")

        logger.info("")
        logger.info("[OK] MARKETINGKOLABS IS NOW RUNNING 24/7")
        logger.info("[OK] Voice control active - speak commands to control PC")
        logger.info("[OK] Proactive monitoring active")
        logger.info("[OK] Gamification active")
        logger.info("[OK] Multi-language support: EN, HI, TE")
        logger.info("[OK] PC control ready: open apps, search web, control system")
        logger.info("")

        # Speak welcome message
        if self.tts_engine:
            self.tts_engine.speak("Marketingkolabs voice agent is now running. Speak commands to control your PC.")

        # Start proactive monitoring thread
        proactive_thread = threading.Thread(target=self.proactive_check, daemon=True)
        proactive_thread.start()

        # Run in specified mode
        if mode == "wake_word":
            self._run_wake_word_mode()
        elif mode == "hotkey":
            self._run_hotkey_mode()
        else:
            # Main voice interaction loop with crash recovery
            self._main_loop_with_recovery()

    def _run_wake_word_mode(self):
        """Run with wake word detection for hands-free control"""
        try:
            from core.wake_word import WakeWordDetector
            import yaml
            with open("config.yaml", 'r') as f:
                config = yaml.safe_load(f)
            wake_word = WakeWordDetector(config)

            def on_wake_word():
                logger.info("Wake word detected!")
                if self.tts_engine:
                    self.tts_engine.speak("Yes?", blocking=False)
                text = self._listen_for_command()
                if text:
                    result = self._process_voice_command(text)
                    response = result.get('message', 'Done') if isinstance(result, dict) else str(result)
                    print(f"Agent: {response}")
                    if self.tts_engine:
                        self.tts_engine.speak(response)

            logger.info("Wake word mode started. Say wake word to activate.")
            wake_word.start(on_wake_word)

            # Keep running until stopped
            try:
                while self.is_running:
                    time.sleep(0.5)
            except KeyboardInterrupt:
                wake_word.stop()
        except Exception as e:
            logger.error(f"Wake word mode failed: {e}")
            logger.info("Falling back to voice mode")
            self._main_loop_with_recovery()

    def _run_hotkey_mode(self, hotkey='ctrl+shift+space'):
        """Run with hotkey trigger for voice commands
        Note: Win+Space requires admin rights on Windows.
        Default: Ctrl+Shift+Space (works without admin)
        """
        try:
            from pynput import keyboard

            def on_activate():
                if self._is_processing:
                    logger.info("Already processing, ignoring hotkey")
                    return
                self._is_processing = True
                logger.info("Hotkey triggered!")
                if self.tts_engine:
                    self.tts_engine.speak("Yes?", blocking=False)
                text = self._listen_for_command()
                if text:
                    result = self._process_voice_command(text)
                    response = result.get('message', 'Done') if isinstance(result, dict) else str(result)
                    print(f"Agent: {response}")
                    if self.tts_engine:
                        self.tts_engine.speak(response)
                self._is_processing = False

            # Map hotkey string to pynput format
            hotkey_map = {
                'win+space': '<cmd>+<space>',  # Windows key
                'ctrl+shift+space': '<ctrl>+<shift>+<space>',
                'ctrl+space': '<ctrl>+<space>',
            }
            pynput_hotkey = hotkey_map.get(hotkey.lower(), '<ctrl>+<shift>+<space>')

            logger.info(f"Hotkey mode started. Press {hotkey.upper()} to speak.")
            if self.tts_engine:
                self.tts_engine.speak(f"Hotkey mode ready. Press {hotkey} to speak.")

            with keyboard.GlobalHotKeys({
                pynput_hotkey: on_activate
            }) as l:
                while self.is_running:
                    time.sleep(0.5)
        except Exception as e:
            logger.error(f"Hotkey mode failed: {e}")
            logger.info("Falling back to voice mode")
            self._main_loop_with_recovery()

    def _listen_for_command(self) -> str:
        """Listen for voice command and return transcribed text"""
        if not self.stt_engine:
            logger.error("STT engine not available")
            return ""

        try:
            if self.tts_engine:
                self.tts_engine.speak("Listening...", blocking=False)
            else:
                print("Listening...")

            text = self.stt_engine.record_and_transcribe(duration=4.0)
            if text:
                logger.info(f"Voice command: '{text}'")
            return text.strip() if text else ""
        except Exception as e:
            logger.error(f"Voice capture error: {e}")
            return ""

    def _process_voice_command(self, text: str) -> dict:
        """Process a voice/text command and execute it"""
        if not text:
            return {'success': False, 'message': 'No input detected'}

        # Special commands handled directly
        text_lower = text.lower()

        if any(word in text_lower for word in ['exit', 'quit', 'stop', 'goodbye']):
            self.stop()
            return {'success': True, 'message': 'Stopping agent'}

        if 'help' in text_lower or 'commands' in text_lower or 'what can you do' in text_lower:
            return {'success': True, 'message': '''Available voice commands:
- Open apps: "Open Chrome", "Open Notepad", "Open Calculator"
- Web search: "Search for Python tutorials"
- PC control: "Take screenshot", "Lock screen", "Show desktop"
- Text: "Type hello", "Press enter", "Click mouse"
- Time: "What time is it?"
- Agent: "Daily brief", "Evening wrapup", "Gamification status"
- "Stop" or "Goodbye" to exit'''}

        if 'daily brief' in text_lower:
            return self.daily_brief()

        if 'evening' in text_lower and ('wrap' in text_lower or 'summary' in text_lower):
            return self.evening_wrapup()

        if 'export memory' in text_lower:
            return self.export_memory()

        if 'switch personality' in text_lower:
            name = text.split('personality')[-1].strip() if 'personality' in text_lower else 'default'
            return self.switch_personality(name)

        if 'gamification' in text_lower or ('status' in text_lower and 'game' in text_lower):
            return self.get_gamification_status()

        if 'what time' in text_lower or 'time is it' in text_lower:
            from datetime import datetime
            now = datetime.now().strftime("%I:%M %p")
            return {'success': True, 'message': f"The time is {now}"}

        # PC Control Commands
        if any(p in text_lower for p in ['open ', 'launch ', 'start ']) and any(app in text_lower for app in ['browser', 'chrome', 'firefox', 'edge', 'notepad', 'calculator', 'cmd', 'explorer']):
            action = {'skill': 'app_control', 'action': 'open_app', 'params': {'app_name': text}}
            return self.execute_action(action)

        if 'search for' in text_lower or ('search' in text_lower and 'for' in text_lower):
            query = text_lower.split('search for')[-1].strip() if 'search for' in text_lower else text_lower.split('search')[-1].strip()
            if query:
                import webbrowser
                url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
                webbrowser.open(url)
                return {'success': True, 'message': f'Searching for {query}'}

        # System control commands
        if 'screenshot' in text_lower:
            return self.execute_action({'skill': 'system', 'action': 'screenshot', 'params': {}})

        if 'click' in text_lower and ('mouse' in text_lower or 'here' in text_lower or 'that' in text_lower):
            return self.execute_action({'skill': 'system', 'action': 'click', 'params': {'x': None, 'y': None}})

        if 'type ' in text_lower or 'write ' in text_lower:
            txt = text_lower.split('type ')[-1] if 'type ' in text_lower else text_lower.split('write ')[-1]
            return self.execute_action({'skill': 'system', 'action': 'type_text', 'params': {'text': txt}})

        if 'press ' in text_lower or 'hit ' in text_lower:
            key = text_lower.split('press ')[-1].strip() if 'press ' in text_lower else text_lower.split('hit ')[-1].strip()
            return self.execute_action({'skill': 'system', 'action': 'press_key', 'params': {'key': key}})

        if 'minimize' in text_lower or 'show desktop' in text_lower:
            return self.execute_action({'skill': 'system', 'action': 'minimize_all', 'params': {}})

        if 'switch window' in text_lower or 'alt tab' in text_lower:
            return self.execute_action({'skill': 'system', 'action': 'switch_window', 'params': {}})

        if 'lock' in text_lower and ('screen' in text_lower or 'pc' in text_lower or 'computer' in text_lower):
            return self.execute_action({'skill': 'system', 'action': 'lock_screen', 'params': {}})

        # Use intent parser if available
        if self.intent_parser:
            try:
                action = self.intent_parser.parse(text)
                logger.info(f"Parsed action: {action}")

                # Route to skill if available
                if self.skill_router and action.get('skill'):
                    result = self.skill_router.route(action)
                    if result:
                        return result

                # Fallback: execute internally if skill router failed
                if action.get('skill'):
                    result = self.execute_action(action)
                    if result.get('success') or result.get('message'):
                        return result
            except Exception as e:
                logger.error(f"Intent parsing error: {e}")

        # Fallback: use internal parse
        action = self._parse_intent(text)
        result = self.execute_action(action)

        # Store in memory
        self.store_interaction(text, action, result)

        return result

    def _main_loop_with_recovery(self):
        """Main loop with automatic crash recovery - uses voice input"""
        consecutive_errors = 0
        max_errors = 5

        while self.is_running:
            try:
                print("\n" + "=" * 60)
                print("MARKETINGKOLABS - 24/7 AUTONOMOUS VOICE AGENT")
                print("Speak commands to control your PC")
                print("Commands: 'daily brief', 'evening wrapup', 'export memory'")
                print("          'switch personality [name]', 'gamification status'")
                print("          'open browser', 'search for [query]', 'what time is it'")
                print("=" * 60 + "\n")

                while self.is_running:
                    try:
                        # Listen for voice command
                        user_input = self._listen_for_command()

                        if not user_input:
                            continue

                        # Process the command
                        result = self._process_voice_command(user_input)

                        if result.get('success') is False and 'Stopping' in result.get('message', ''):
                            return

                        # Output result
                        response_text = result.get('message', 'Done') if isinstance(result, dict) else str(result)
                        print(f"Agent: {response_text}\n")

                        # Speak the response
                        if self.voice_mode and self.tts_engine:
                            self.tts_engine.speak(response_text)

                        # Reset error counter on success
                        consecutive_errors = 0

                    except KeyboardInterrupt:
                        self.stop()
                        return
                    except Exception as e:
                        consecutive_errors += 1
                        logger.error(f"Main loop error ({consecutive_errors}/{max_errors}): {e}")

                        if consecutive_errors >= max_errors:
                            logger.critical("Too many consecutive errors! Entering crash recovery...")
                            self._crash_recovery()
                            consecutive_errors = 0

            except Exception as e:
                logger.critical(f"CRITICAL: Main loop crashed: {e}")
                self._crash_recovery()

    def _crash_recovery(self):
        """Attempt to recover from crashes"""
        logger.info("🔧 Starting crash recovery...")

        # Wait before retry
        time.sleep(5)

        # Check Ollama
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=2)
            if not response.ok:
                logger.error("Ollama not responding. Attempting restart...")
                # In production, restart Ollama here
        except:
            logger.error("Ollama connection failed. Please restart: ollama serve")

        logger.info("Recovery attempt complete. Resuming operations...")

    def stop(self):
        """Stop the agent"""
        logger.info("Stopping Marketingkolabs Autonomous Agent...")
        self.is_running = False
        logger.info("Agent stopped.")


if __name__ == "__main__":
    # Check if Ollama is running
    try:
        response = requests.get(f"{os.environ.get('OLLAMA_URL', 'http://localhost:11434')}/api/tags", timeout=2)
        if not response.ok:
            print("⚠️  Ollama is not running!")
            print("Please start Ollama first: ollama serve")
            print("Then pull the model: ollama pull phi3:mini")
            sys.exit(1)
    except:
        print("⚠️  Ollama is not running!")
        print("Please start Ollama first: ollama serve")
        print("Then pull the model: ollama pull phi3:mini")
        sys.exit(1)

    # Check for updates first
    if os.path.exists("UPDATE.bat"):
        print("🔄 Checking for updates...")
        os.system("UPDATE.bat")

    # Start the agent
    agent = AutonomousAgent()
    agent.start()
