"""
MARKETINGKOLABS VOICE AGENT - WORKING VERSION
- Simple, no threading crashes
- Clear visual + voice feedback
- Type or speak commands
"""
import os
import sys
import time
import subprocess
import threading
import queue
import logging
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('agent.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ============ SIMPLE TTS (No Crashes) ============
class SimpleTTS:
    """TTS that works - uses a queue to avoid threading issues"""

    def __init__(self):
        self.queue = queue.Queue()
        self.running = True
        self.engine = None
        self.personality = 'default'

        # Personalities
        self.personalities = {
            'default': {'rate': 150, 'prefix': '', 'suffix': ''},
            'jarvis': {'rate': 130, 'prefix': 'Sir, ', 'suffix': '. At your service.'},
            'friday': {'rate': 180, 'prefix': 'Boss, ', 'suffix': '. Done.'},
        }

        # Init engine
        try:
            import pyttsx3
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 150)
            voices = self.engine.getProperty('voices')
            if voices:
                for v in voices:
                    if 'en' in v.id.lower() and 'female' not in v.id.lower():
                        self.engine.setProperty('voice', v.id)
                        break
            logger.info("[TTS] Ready")
        except Exception as e:
            logger.error(f"[TTS] Failed: {e}")
            self.engine = None

        # Start TTS worker thread
        self.worker = threading.Thread(target=self._tts_worker, daemon=True)
        self.worker.start()

    def _tts_worker(self):
        """Single thread handles all TTS - no crashes"""
        while self.running:
            try:
                text = self.queue.get(timeout=0.5)
                if text is None:
                    break
                if self.engine:
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except:
                        pass
            except queue.Empty:
                pass

    def speak(self, text: str):
        """Queue text for speaking"""
        if not text or not self.engine:
            return
        p = self.personalities.get(self.personality, self.personalities['default'])
        styled = f"{p['prefix']}{text}{p['suffix']}"
        self.queue.put(styled)

    def set_personality(self, name: str):
        if name in self.personalities:
            self.personality = name
            if self.engine:
                self.engine.setProperty('rate', self.personalities[name]['rate'])
            return True
        return False


# ============ SIMPLE STT ============
class SimpleSTT:
    """STT that works - VAD recording"""

    def __init__(self):
        self.model = None
        self.mic_id = None

        try:
            from faster_whisper import WhisperModel
            self.model = WhisperModel('tiny', device='cpu', compute_type='int8')
            logger.info("[STT] Whisper ready")
        except Exception as e:
            logger.error(f"[STT] Failed: {e}")

        try:
            import sounddevice as sd
            self.sd = sd
            # Find Bluetooth mic
            devices = sd.query_devices()
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
            logger.info(f"[STT] Mic: {self.mic_id}")
        except Exception as e:
            logger.error(f"[STT] Mic failed: {e}")
            self.sd = None

    def listen(self, timeout: float = 5.0) -> str:
        """Listen and transcribe"""
        if not self.model or not self.sd:
            logger.error("[STT] Not ready")
            return ""

        try:
            import numpy as np
            import webrtcvad

            vad = webrtcvad.Vad(2)
            chunks = []
            speaking = False
            silence_start = None

            def callback(indata, frames, time_info, status):
                chunks.append(indata.copy())

            logger.info("[LISTENING... Speak now!]")
            print("\n" + "="*50)
            print("  [LISTENING... Speak now!]")
            print("="*50)

            with self.sd.InputStream(
                device=self.mic_id,
                samplerate=16000,
                channels=1,
                dtype='int16',
                blocksize=480,  # 30ms
                callback=callback
            ):
                start = time.time()
                while (time.time() - start) < timeout:
                    time.sleep(0.05)
                    if len(chunks) > 5:
                        chunk = chunks[-1]
                        try:
                            is_speech = vad.is_speech((chunk / 32768.0).astype(np.float32).tobytes(), 16000)
                            if is_speech:
                                speaking = True
                                silence_start = None
                            elif speaking:
                                if silence_start is None:
                                    silence_start = time.time()
                                elif (time.time() - silence_start) > 1.0:
                                    break
                        except:
                            pass

            if chunks:
                audio = (np.concatenate(chunks) / 32768.0).astype(np.float32)
                segments, _ = self.model.transcribe(audio, language='en', vad_filter=False)
                text = " ".join(s.text for s in segments).strip()
                if text:
                    logger.info(f"[HEARD] '{text}'")
                    print(f"\n[YOU SAID]: {text}\n")
                    return text

            logger.warning("[NO SPEECH DETECTED]")
            return ""

        except ImportError:
            # Fallback: fixed recording
            try:
                import numpy as np
                logger.info("[LISTENING... Speak now!] (no VAD)")
                print("\n[LISTENING... Speak now!]")
                recording = self.sd.rec(int(16000 * 4), samplerate=16000, channels=1, dtype='float32', device=self.mic_id)
                self.sd.wait()
                if self.model:
                    segments, _ = self.model.transcribe(recording.flatten(), language='en')
                    text = " ".join(s.text for s in segments).strip()
                    if text:
                        logger.info(f"[HEARD] '{text}'")
                        return text
            except Exception as e:
                logger.error(f"[STT] Error: {e}")
        except Exception as e:
            logger.error(f"[STT] Error: {e}")

        return ""


# ============ COMMAND PROCESSOR ============
class CommandProcessor:
    """Process voice commands"""

    def __init__(self, tts, stt):
        self.tts = tts
        self.stt = stt
        self.xp = 0
        self.level = 1

    def process(self, text: str) -> str:
        """Process command and return response"""
        if not text:
            return "No input"

        text_lower = text.lower()
        logger.info(f"[COMMAND] Processing: '{text}'")

        # Exit
        if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
            return "STOP"

        # Help
        if 'help' in text_lower or 'what can you do' in text_lower:
            return """Available commands:
- Open Chrome / Notepad / Calculator
- Search for [query]
- Type [text] / Press [key]
- Take screenshot / Lock screen
- Show desktop / Switch window
- What time is it? / What day is it?
- Switch personality [jarvis/friday]
- Help / Stop"""

        # Personality
        if 'switch personality' in text_lower or 'change voice' in text_lower:
            for p in ['jarvis', 'friday']:
                if p in text_lower:
                    if self.tts.set_personality(p):
                        return f"Switched to {p} personality"
            return f"Available: jarvis, friday"

        # Time
        if 'what time' in text_lower or 'time is it' in text_lower:
            now = datetime.now().strftime("%I:%M %p")
            return f"The time is {now}"

        # Date
        if 'what day' in text_lower or 'what date' in text_lower:
            now = datetime.now().strftime("%A, %B %d, %Y")
            return f"Today is {now}"

        # Open apps
        for trigger in ['open ', 'launch ', 'start ']:
            if trigger in text_lower:
                app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
                if app:
                    return self._open_app(app)

        # Search
        if 'search for ' in text_lower:
            query = text_lower.split('search for ')[-1].strip()
            if query:
                return self._search(query)

        # Type text
        for trigger in ['type ', 'write ']:
            if trigger in text_lower:
                txt = text.split(trigger)[-1].strip()
                if txt:
                    return self._type_text(txt)

        # Press key
        for trigger in ['press ', 'hit ']:
            if trigger in text_lower:
                key = text_lower.split(trigger)[-1].strip()
                if key:
                    return self._press_key(key)

        # Screenshot
        if 'screenshot' in text_lower or 'capture screen' in text_lower:
            return self._screenshot()

        # Lock screen
        if 'lock' in text_lower and ('screen' in text_lower or 'pc' in text_lower):
            return self._lock_screen()

        # Show desktop
        if 'show desktop' in text_lower or 'minimize all' in text_lower:
            return self._press_key('win+d')

        # Switch window
        if 'switch window' in text_lower or 'alt tab' in text_lower:
            return self._press_key('alt+tab')

        # Gamification
        if 'gamification' in text_lower or 'status' in text_lower or 'xp' in text_lower:
            return f"Level {self.level}, XP: {self.xp}/100 to next level"

        # Fallback
        return "Sorry, I didn't understand. Say 'Help' for commands."

    def _open_app(self, app: str) -> str:
        """Open application"""
        app_map = {
            'chrome': 'chrome', 'google chrome': 'chrome', 'browser': 'chrome',
            'firefox': 'firefox', 'edge': 'msedge', 'notepad': 'notepad',
            'calculator': 'calc', 'cmd': 'cmd', 'explorer': 'explorer',
        }
        exe = app_map.get(app, app)

        try:
            subprocess.Popen(f'start "" "{exe}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.xp += 10
            return f"Opened {app}"
        except:
            try:
                subprocess.Popen(f'start "" "{exe}.exe"', shell=True)
                self.xp += 10
                return f"Opened {app}"
            except Exception as e:
                return f"Failed to open {app}: {e}"

    def _search(self, query: str) -> str:
        """Search web"""
        try:
            import webbrowser
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            webbrowser.open(url)
            self.xp += 5
            return f"Searching for {query}"
        except Exception as e:
            return f"Search failed: {e}"

    def _type_text(self, text: str) -> str:
        """Type text"""
        try:
            import pyautogui
            pyautogui.write(text)
            return f"Typed: {text}"
        except Exception as e:
            return f"Type failed: {e}"

    def _press_key(self, key: str) -> str:
        """Press key"""
        try:
            import pyautogui
            if '+' in key:
                keys = [k.strip() for k in key.split('+')]
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(key)
            return f"Pressed: {key}"
        except Exception as e:
            return f"Press failed: {e}"

    def _screenshot(self) -> str:
        """Take screenshot"""
        try:
            import pyautogui
            path = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            pyautogui.screenshot().save(path)
            self.xp += 5
            return f"Screenshot saved: {path}"
        except Exception as e:
            return f"Screenshot failed: {e}"

    def _lock_screen(self) -> str:
        """Lock screen"""
        try:
            subprocess.Popen('rundll32.exe user32.dll,LockWorkStation')
            return "Screen locked"
        except Exception as e:
            return f"Lock failed: {e}"


# ============ MAIN ============
def main():
    print("\n" + "="*60)
    print("  MARKETINGKOLABS VOICE AGENT - WORKING VERSION")
    print("="*60)
    print()

    # Init
    logger.info("[INIT] Starting...")
    tts = SimpleTTS()
    stt = SimpleSTT()
    processor = CommandProcessor(tts, stt)

    print("\n" + "="*60)
    print("  READY! Choose mode:")
    print("  1. Type commands (type 'voice' to switch to voice)")
    print("  2. Voice mode (type 'voice' to start)")
    print("  3. Say 'Help' for commands")
    print("="*60 + "\n")

    tts.speak("System ready. Type commands or say voice for voice mode.")

    mode = 'text'  # text or voice

    while True:
        try:
            if mode == 'text':
                try:
                    user_input = input("[YOU] ").strip()
                except EOFError:
                    break

                if not user_input:
                    continue

                if user_input.lower() == 'voice':
                    mode = 'voice'
                    print("\n[SWITCHED TO VOICE MODE]")
                    print("[Say 'Stop' to exit, 'Type' to switch back]\n")
                    tts.speak("Voice mode activated. Speak commands.", blocking=False)
                    continue

                if user_input.lower() == 'type':
                    mode = 'text'
                    print("\n[SWITCHED TO TEXT MODE]\n")
                    continue

                result = processor.process(user_input)

                if result == "STOP":
                    print("\n[STOPPING...]\n")
                    tts.speak("Goodbye!", blocking=True)
                    break

                print(f"[AGENT] {result}\n")
                tts.speak(result, blocking=False)

            else:  # voice mode
                text = stt.listen()
                if text:
                    result = processor.process(text)

                    if result == "STOP":
                        print("\n[STOPPING...]\n")
                        tts.speak("Goodbye!", blocking=True)
                        break

                    print(f"[AGENT] {result}\n")
                    tts.speak(result, blocking=False)

                    # Check for mode switch
                    if 'type' in text.lower():
                        mode = 'text'
                        print("\n[SWITCHED TO TEXT MODE]\n")
                        continue

        except KeyboardInterrupt:
            print("\n\n[STOPPED]\n")
            tts.speak("Goodbye!", blocking=True)
            break
        except Exception as e:
            logger.error(f"[ERROR] {e}")
            time.sleep(1)


if __name__ == "__main__":
    main()
