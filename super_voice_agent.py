"""
MARKETINGKOLABS SUPERPOWER VOICE AGENT
- Full PC Control via Voice
- Wake Word + Hotkey + Continuous Modes
- Vision (Screen Understanding)
- Premium UI with Real-time Feedback
- Unique Voice Personalities
- 100% Local, No Cloud
"""
import os
import sys
import time
import json
import sqlite3
import subprocess
import threading
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('super_agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ VOICE ENGINE ============
class VoiceEngine:
    """Unified voice engine with TTS + STT + Personalities"""

    PERSONALITIES = {
        'default': {'rate': 150, 'volume': 1.0, 'prefix': '', 'suffix': ''},
        'jarvis': {'rate': 130, 'volume': 0.8, 'prefix': 'Sir, ', 'suffix': '. At your service.'},
        'friday': {'rate': 180, 'volume': 1.0, 'prefix': 'Boss, ', 'suffix': '. Done.'},
        'ghost': {'rate': 100, 'volume': 0.6, 'prefix': '[Whisper] ', 'suffix': ''},
        'nova': {'rate': 200, 'volume': 1.0, 'prefix': '* ', 'suffix': ' *'},
        'commander': {'rate': 120, 'volume': 1.0, 'prefix': 'Commander, ', 'suffix': '. Execute.'},
    }

    def __init__(self):
        # TTS
        try:
            import pyttsx3
            self.tts = pyttsx3.init()
            self.tts.setProperty('rate', 150)
            voices = self.tts.getProperty('voices')
            if voices:
                for v in voices:
                    if 'en' in v.id.lower() and 'female' not in v.id.lower():
                        self.tts.setProperty('voice', v.id)
                        break
        except:
            self.tts = None

        # STT
        try:
            from faster_whisper import WhisperModel
            self.stt_model = WhisperModel('tiny', device='cpu', compute_type='int8')
        except:
            self.stt_model = None

        # Microphone
        try:
            import sounddevice as sd
            self.sd = sd
            # Auto-detect best mic (prefer Bluetooth)
            devices = sd.query_devices()
            self.mic_id = None
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0:
                    name = dev['name'].lower()
                    if 'bluetooth' in name or 'headset' in name or 'airbass' in name:
                        self.mic_id = i
                        break
            if self.mic_id is None:
                for i, dev in enumerate(devices):
                    if dev['max_input_channels'] > 0 and dev.get('default'):
                        self.mic_id = i
                        break
        except:
            self.sd = None
            self.mic_id = None

        self.current_personality = 'default'
        self._lock = threading.Lock()

    def speak(self, text: str, blocking: bool = False):
        """Speak with personality - simplified to avoid threading issues"""
        if not self.tts or not text:
            return

        p = self.PERSONALITIES.get(self.current_personality, self.PERSONALITIES['default'])
        styled = f"{p['prefix']}{text}{p['suffix']}"

        try:
            # Stop any current speech
            try:
                self.tts.stop()
            except:
                pass

            # Use blocking mode to avoid threading issues
            if blocking:
                self.tts.say(styled)
                self.tts.runAndWait()
            else:
                # Non-blocking: use a fresh engine instance
                def _speak_blocking():
                    try:
                        import pyttsx3
                        eng = pyttsx3.init()
                        eng.setProperty('rate', p['rate'])
                        eng.setProperty('volume', p['volume'])
                        eng.say(styled)
                        eng.runAndWait()
                    except:
                        pass
                threading.Thread(target=_speak_blocking, daemon=True).start()
        except Exception as e:
            logger.error(f"TTS error: {e}")

    def set_personality(self, name: str):
        if name in self.PERSONALITIES and self.tts:
            self.current_personality = name
            self.tts.setProperty('rate', self.PERSONALITIES[name]['rate'])
            self.tts.setProperty('volume', self.PERSONALITIES[name]['volume'])
            return True
        return False

    def listen(self, timeout: float = 5.0) -> str:
        """Listen and transcribe with VAD - stops when you stop speaking"""
        if not self.stt_model or not self.sd:
            return ""

        try:
            import numpy as np
            import webrtcvad

            vad = webrtcvad.Vad(2)
            chunk_duration = 0.03
            chunks = []
            speaking = False
            silence_start = None
            speech_detected = False

            def callback(indata, frames, time_info, status):
                if status:
                    pass
                chunks.append(indata.copy())

            with self.sd.InputStream(
                device=self.mic_id,
                samplerate=16000,
                channels=1,
                dtype='int16',
                blocksize=int(16000 * chunk_duration),
                callback=callback
            ):
                start = time.time()

                while (time.time() - start) < timeout:
                    time.sleep(0.05)
                    if len(chunks) > 5:
                        chunk = chunks[-1]
                        try:
                            is_speech = vad.is_speech(chunk.tobytes(), 16000)
                            if is_speech:
                                speaking = True
                                speech_detected = True
                                silence_start = None
                            elif speaking:
                                if silence_start is None:
                                    silence_start = time.time()
                                elif (time.time() - silence_start) > 1.0:  # 1s silence = done
                                    break
                        except:
                            pass

            if chunks and speech_detected:
                audio = np.concatenate(chunks)
                audio_f32 = (audio / 32768.0).astype(np.float32)
                segments, _ = self.stt_model.transcribe(audio_f32, language='en', vad_filter=False)
                text = " ".join(s.text for s in segments).strip()
                # Clean up repetition (fixes "a little bit of a little bit...")
                if text:
                    words = text.split()
                    if len(words) > 6:
                        # Remove repetitive phrases
                        text = ' '.join(dict.fromkeys(words).keys())  # rough dedup
                return text

        except ImportError:
            # Fallback: fixed 4s recording
            try:
                import numpy as np
                recording = self.sd.rec(
                    int(16000 * 4), samplerate=16000, channels=1, dtype='float32', device=self.mic_id
                )
                self.sd.wait()
                if self.stt_model:
                    segments, _ = self.stt_model.transcribe(recording.flatten(), language='en')
                    return " ".join(s.text for s in segments).strip()
            except Exception as e:
                logger.error(f"Fallback recording error: {e}")
        except Exception as e:
            logger.error(f"Listen error: {e}")

        return ""


# ============ PC CONTROL ============
class PCController:
    """Full PC control via voice"""

    def __init__(self):
        try:
            import pyautogui
            self.pyautogui = pyautogui
        except:
            self.pyautogui = None

    def open_app(self, name: str) -> dict:
        """Open any application"""
        app_map = {
            'chrome': 'chrome', 'google chrome': 'chrome', 'browser': 'chrome',
            'firefox': 'firefox', 'edge': 'msedge', 'microsoft edge': 'msedge',
            'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
            'command prompt': 'cmd', 'explorer': 'explorer', 'file explorer': 'explorer',
            'paint': 'mspaint', 'word': 'winword', 'excel': 'excel',
            'settings': 'ms-settings:', 'control panel': 'control',
            'spotify': 'spotify', 'discord': 'discord',
        }
        app = app_map.get(name.lower(), name.lower())

        try:
            subprocess.Popen(f'start "" "{app}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return {'success': True, 'message': f'Opened {name}'}
        except:
            try:
                subprocess.Popen(f'start "" "{app}.exe"', shell=True)
                return {'success': True, 'message': f'Opened {name}'}
            except Exception as e:
                return {'success': False, 'message': f'Failed: {e}'}

    def search_web(self, query: str) -> dict:
        """Search the web"""
        try:
            import webbrowser
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            return {'success': True, 'message': f'Searching: {query}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def type_text(self, text: str) -> dict:
        """Type text"""
        if not self.pyautogui:
            return {'success': False, 'message': 'pyautogui not installed'}
        try:
            self.pyautogui.write(text)
            return {'success': True, 'message': f'Typed: {text}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def press_key(self, key: str) -> dict:
        """Press a key or key combination"""
        if not self.pyautogui:
            return {'success': False, 'message': 'pyautogui not installed'}
        try:
            if '+' in key:
                keys = [k.strip() for k in key.split('+')]
                self.pyautogui.hotkey(*keys)
            else:
                self.pyautogui.press(key)
            return {'success': True, 'message': f'Pressed: {key}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def click(self, x: int = None, y: int = None) -> dict:
        """Click at position or current position"""
        if not self.pyautogui:
            return {'success': False, 'message': 'pyautogui not installed'}
        try:
            if x is not None and y is not None:
                self.pyautogui.click(x=x, y=y)
            else:
                self.pyautogui.click()
            return {'success': True, 'message': 'Clicked'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def screenshot(self) -> dict:
        """Take screenshot"""
        if not self.pyautogui:
            return {'success': False, 'message': 'pyautogui not installed'}
        try:
            path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            img = self.pyautogui.screenshot()
            img.save(path)
            return {'success': True, 'message': f'Saved: {path}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    def lock_screen(self) -> dict:
        """Lock the screen"""
        try:
            subprocess.Popen('rundll32.exe user32.dll,LockWorkStation')
            return {'success': True, 'message': 'Screen locked'}
        except Exception as e:
            return {'success': False, 'message': str(e)}


# ============ SCREEN UNDERSTANDING ============
class ScreenUnderstanding:
    """Understand what's on screen using Ollama vision"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434"

    def analyze(self, question: str = "What's on my screen?") -> dict:
        """Analyze screen with vision model"""
        try:
            import pyautogui
            import base64
            from io import BytesIO

            # Take screenshot
            screenshot = pyautogui.screenshot()
            buffer = BytesIO()
            screenshot.save(buffer, format='PNG')
            img_b64 = base64.b64encode(buffer.getvalue()).decode()

            # Try vision model
            import requests
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": "llava",
                    "prompt": question,
                    "images": [img_b64],
                    "stream": False,
                    "options": {"temperature": 0.1}
                },
                timeout=30
            )

            if response.ok:
                result = response.json().get('response', '').strip()
                if result:
                    return {'success': True, 'message': result}

            # Fallback: describe window
            try:
                win = pyautogui.getActiveWindow()
                return {'success': True, 'message': f'Active window: {win.title if win else "Unknown"}'}
            except:
                return {'success': False, 'message': 'Vision model not available'}

        except Exception as e:
            return {'success': False, 'message': str(e)}


# ============ SUPER AGENT ============
class SuperVoiceAgent:
    """The ultimate voice-controlled PC agent"""

    def __init__(self):
        self.voice = VoiceEngine()
        self.pc = PCController()
        self.vision = ScreenUnderstanding()
        self.is_running = False
        self._processing = False

        # Gamification
        self.xp = 0
        self.level = 1

        logger.info("=" * 60)
        logger.info("MARKETINGKOLABS SUPERPOWER AGENT")
        logger.info("=" * 60)
        logger.info(f"[OK] Voice: {self.voice.mic_id or 'default'} mic")
        logger.info(f"[OK] TTS: {'Ready' if self.voice.tts else 'Failed'}")
        logger.info(f"[OK] STT: {'Ready' if self.voice.stt_model else 'Failed'}")
        logger.info(f"[OK] PC Control: {'Ready' if self.pc.pyautogui else 'Limited'}")
        logger.info("=" * 60)

    def process_command(self, text: str) -> dict:
        """Process any voice command"""
        if not text:
            return {'success': False, 'message': 'No input'}

        text_lower = text.lower()
        logger.info(f"Command: '{text}'")

        # Exit commands
        if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
            self.stop()
            return {'success': True, 'message': 'Stopping'}

        # Help
        if 'help' in text_lower or 'what can you do' in text_lower:
            return {'success': True, 'message': '''Superpowers:
- "Open Chrome/Firefox/Notepad/Calculator"
- "Search for [anything]"
- "Type [text]" / "Press [key]"
- "Click mouse" / "Take screenshot"
- "What's on my screen?" (vision)
- "Lock screen" / "Show desktop"
- "What time is it?" / "Gamification status"
- "Switch personality [jarvis/friday/ghost/nova]"
- "Stop" to exit'''}

        # Personalities
        if 'switch personality' in text_lower or 'change voice' in text_lower:
            for p in self.voice.PERSONALITIES.keys():
                if p in text_lower:
                    if self.voice.set_personality(p):
                        return {'success': True, 'message': f'Switched to {p} personality'}
            return {'success': False, 'message': f'Available: {list(self.voice.PERSONALITIES.keys())}'}

        # Time
        if 'what time' in text_lower or 'time is it' in text_lower:
            now = datetime.now().strftime("%I:%M %p")
            return {'success': True, 'message': f'The time is {now}'}

        # Date
        if 'what date' in text_lower or 'what day' in text_lower:
            now = datetime.now().strftime("%A, %B %d, %Y")
            return {'success': True, 'message': f'Today is {now}'}

        # Open apps
        for trigger in ['open ', 'launch ', 'start ']:
            if trigger in text_lower:
                app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
                if app:
                    result = self.pc.open_app(app)
                    if result['success']:
                        self.add_xp(10)
                    return result

        # Search
        if 'search for ' in text_lower:
            query = text_lower.split('search for ')[-1].strip()
            if query:
                self.add_xp(5)
                return self.pc.search_web(query)

        # Type text
        for trigger in ['type ', 'write ']:
            if trigger in text_lower:
                txt = text.split(trigger)[-1].strip()
                if txt:
                    return self.pc.type_text(txt)

        # Press key
        for trigger in ['press ', 'hit ']:
            if trigger in text_lower:
                key = text_lower.split(trigger)[-1].strip()
                if key:
                    return self.pc.press_key(key)

        # Click
        if 'click' in text_lower and ('mouse' in text_lower or 'here' in text_lower):
            return self.pc.click()

        # Screenshot
        if 'screenshot' in text_lower or 'capture screen' in text_lower:
            self.add_xp(5)
            return self.pc.screenshot()

        # Lock screen
        if 'lock' in text_lower and ('screen' in text_lower or 'pc' in text_lower):
            return self.pc.lock_screen()

        # Show desktop
        if 'show desktop' in text_lower or 'minimize all' in text_lower:
            return self.pc.press_key('win+d')

        # Alt+Tab
        if 'switch window' in text_lower or 'alt tab' in text_lower:
            return self.pc.press_key('alt+tab')

        # Vision / Screen understanding
        if 'screen' in text_lower and any(w in text_lower for w in ['what', 'see', 'on my', 'analyze']):
            self.add_xp(15)
            return self.vision.analyze("What's on my screen? Describe the content.")

        if 'selected text' in text_lower or 'what did i select' in text_lower:
            return self.vision.analyze("What text is currently selected or visible?")

        # Gamification
        if 'gamification' in text_lower or 'status' in text_lower or 'xp' in text_lower:
            return {'success': True, 'message': f'Level {self.level}, XP: {self.xp}/100 to next level'}

        # Fallback: Ollama
        try:
            import requests
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "phi3:mini",
                    "prompt": f"Parse this command and respond helpfully: {text}",
                    "stream": False
                },
                timeout=10
            )
            if response.ok:
                answer = response.json().get('response', '').strip()
                if answer:
                    return {'success': True, 'message': answer}
        except:
            pass

        return {'success': False, 'message': "Sorry, I didn't understand that. Say 'Help' for commands."}

    def add_xp(self, amount: int):
        """Add XP and level up"""
        self.xp += amount
        new_level = (self.xp // 100) + 1
        if new_level > self.level:
            self.level = new_level
            self.voice.speak(f"Level up! You're now level {self.level}!")

    def stop(self):
        """Stop the agent"""
        self.is_running = False
        logger.info("Agent stopped")

    def run_voice_mode(self):
        """Continuous voice mode"""
        self.is_running = True
        self.voice.speak("Superpower agent online. Speak commands to control your PC.", blocking=False)

        while self.is_running:
            try:
                print("\n[Listening...]")
                text = self.voice.listen()
                if text:
                    print(f"You: {text}")
                    result = self.process_command(text)
                    msg = result.get('message', 'Done')
                    print(f"Agent: {msg}\n")
                    self.voice.speak(msg)
                elif self._processing:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                time.sleep(1)

        self.stop()

    def run_hotkey_mode(self, hotkey: str = 'ctrl+shift+space'):
        """Hotkey-triggered voice mode"""
        try:
            from pynput import keyboard

            def on_activate():
                if self._processing:
                    return
                self._processing = True
                self.voice.speak("Yes?", blocking=False)
                text = self.voice.listen()
                if text:
                    result = self.process_command(text)
                    self.voice.speak(result.get('message', 'Done'))
                self._processing = False

            # Map hotkey
            hotkey_map = {
                'ctrl+shift+space': '<ctrl>+<shift>+<space>',
                'win+space': '<cmd>+<space>',
                'ctrl+space': '<ctrl>+<space>',
            }
            hk = hotkey_map.get(hotkey.lower(), '<ctrl>+<shift>+<space>')

            self.voice.speak(f"Hotkey mode ready. Press {hotkey} to speak.", blocking=False)
            logger.info(f"Hotkey mode: {hotkey}")

            with keyboard.GlobalHotKeys({hk: on_activate}) as l:
                self.is_running = True
                while self.is_running:
                    time.sleep(0.5)

        except Exception as e:
            logger.error(f"Hotkey mode failed: {e}")
            logger.info("Falling back to voice mode")
            self.run_voice_mode()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', choices=['voice', 'hotkey'], default='voice')
    parser.add_argument('--hotkey', default='ctrl+shift+space')
    args = parser.parse_args()

    # Fix console encoding for Windows
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    agent = SuperVoiceAgent()

    if args.mode == 'hotkey':
        agent.run_hotkey_mode(args.hotkey)
    else:
        agent.run_voice_mode()
