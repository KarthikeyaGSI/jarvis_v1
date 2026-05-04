"""
JARVIS SUPER AGENT - SMART FLOW MODE
Detects active app, finds cursor position, auto-pastes into correct field
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import threading
import re

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

print("\n" + "="*60)
print("  JARVIS - SMART FLOW MODE")
print("="*60)
print(f"[INIT] Working from: {SCRIPT_DIR}")
print("[INIT] Loading Smart Flow features...\n")

# ========= Auto-Import =========
def safe_import(module_name, pip_name=None):
    try:
        return __import__(module_name)
    except ImportError:
        pip_name = pip_name or module_name
        print(f"[AUTO-INSTALL] Installing {pip_name}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name, '-q'], 
                          capture_output=True, timeout=60)
            print(f"[OK] {pip_name} installed!")
            return __import__(module_name)
        except:
            print(f"[FAIL] Could not install {pip_name}")
            return None

# Import with auto-install
pyttsx3 = safe_import('pyttsx3')
faster_whisper = safe_import('faster_whisper', 'faster-whisper')
pyautogui = safe_import('pyautogui', 'pyautogui')
psutil = safe_import('psutil', 'psutil')
tkinter = safe_import('tkinter')

# ========= Active Window Detection =========
print("\n[WINDOW] Initializing active window detection...")

def get_active_window_info():
    """Get active window title and process name"""
    try:
        import win32gui
        import win32process
        import win32api
        
        hwnd = win32gui.GetForegroundWindow()
        window_title = win32gui.GetWindowText(hwnd)
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            import psutil
            process = psutil.Process(pid)
            process_name = process.name()
        except:
            process_name = "unknown"
        
        return {
            'title': window_title,
            'process': process_name,
            'hwnd': hwnd
        }
    except ImportError:
        # Fallback: try pygetwindow if available
        try:
            import pygetwindow as pgw
            win = pgw.getActiveWindow()
            if win:
                return {
                    'title': win.title,
                    'process': win.process,
                    'hwnd': None
                }
        except:
            pass
        
        # Final fallback
        return {
            'title': 'unknown',
            'process': 'unknown',
            'hwnd': None
        }

def get_cursor_position():
    """Get current cursor position (x, y)"""
    try:
        import pyautogui
        return pyautogui.position()
    except:
        return None

def click_at_cursor():
    """Click at current cursor position"""
    try:
        import pyautogui
        pos = pyautogui.position()
        pyautogui.click(pos)
        return pos
    except:
        return None

def type_at_cursor(text, typing_speed=0.01):
    """Type text at current cursor position"""
    try:
        import pyautogui
        time.sleep(0.5)  # Small delay to ensure focus
        pyautogui.write(text, interval=typing_speed)
        return True
    except Exception as e:
        print(f"[TYPE ERROR] {e}")
        return False

def paste_at_cursor(text):
    """Copy text to clipboard and paste at cursor"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        
        time.sleep(0.3)
        
        # Press Ctrl+V to paste
        import pyautogui
        pyautogui.hotkey('ctrl', 'v')
        return True
    except Exception as e:
        print(f"[PASTE ERROR] {e}")
        return False

# ========= App-Specific Behavior =========
APP_CONFIGS = {
    'chrome.exe': {
        'name': 'Chrome',
        'type_method': 'paste',  # Use paste for browser fields
        'need_click': True,
        'url_bar_hotkey': 'ctrl+l'  # Ctrl+L to focus URL bar
    },
    'msedge.exe': {
        'name': 'Edge',
        'type_method': 'paste',
        'need_click': True,
    },
    'notepad.exe': {
        'name': 'Notepad',
        'type_method': 'type',  # Direct typing works
        'need_click': False,
    },
    'winword.exe': {
        'name': 'Word',
        'type_method': 'paste',
        'need_click': False,
    },
    'excel.exe': {
        'name': 'Excel',
        'type_method': 'paste',
        'need_click': False,
    },
    'outlook.exe': {
        'name': 'Outlook',
        'type_method': 'paste',
        'need_click': True,
    },
    'whatsapp.exe': {
        'name': 'WhatsApp',
        'type_method': 'paste',
        'need_click': True,
    },
    'slack.exe': {
        'name': 'Slack',
        'type_method': 'paste',
        'need_click': True,
    },
    'default': {
        'name': 'Unknown App',
        'type_method': 'paste',  # Safer to use paste
        'need_click': True,
    }
}

def get_app_config(process_name):
    """Get configuration for specific app"""
    process_lower = process_name.lower()
    for key, config in APP_CONFIGS.items():
        if key.lower() in process_lower:
            return config
    return APP_CONFIGS['default']

# ========= Smart Flow Mode =========
def smart_flow_mode(duration=30):
    """Smart Flow: Detect app, find cursor, auto-paste text"""
    print(f"\n[SMART FLOW] Starting {duration}-second dictation...")
    print("[SMART FLOW] Focus the field where you want text, then speak naturally!")
    
    # Check if STT is available
    if 'stt_model' not in globals() or not stt_model:
        return "STT not available for Smart Flow, Sir."
    
    try:
        import sounddevice as sd
        import numpy as np
        
        # Step 1: Get initial cursor position (user should have focused the field)
        print("\n[SMART FLOW] Detecting active window and cursor position...")
        time.sleep(1)
        
        window_info = get_active_window_info()
        cursor_pos = get_cursor_position()
        
        print(f"[SMART FLOW] Active app: {window_info['process']}")
        print(f"[SMART FLOW] Window: {window_info['title'][:50]}...")
        if cursor_pos:
            print(f"[SMART FLOW] Cursor position: {cursor_pos}")
        
        config = get_app_config(window_info['process'])
        print(f"[SMART FLOW] Using {config['name']} config: {config['type_method']} method")
        
        # Step 2: Record speech
        print(f"\n[SMART FLOW] Recording for {duration} seconds... SPEAK NOW!")
        
        recording = sd.rec(
            int(16000 * duration),
            samplerate=16000,
            channels=1,
            dtype='float32',
            device=mic_id if 'mic_id' in globals() else None
        )
        sd.wait()
        
        segments, _ = stt_model.transcribe(recording.flatten(), language='en', vad_filter=False)
        raw_text = " ".join(s.text for s in segments).strip()
        
        if not raw_text:
            return "No speech detected in Smart Flow, Sir."
        
        print(f"\n[SMART FLOW] Raw: {raw_text[:100]}...")
        
        # Step 3: Polish with AI
        polished = polish_speech(raw_text)
        print(f"[SMART FLOW] Polished: {polished[:100]}...")
        
        # Step 4: Click back at cursor position if needed
        if config['need_click']:
            print(f"\n[SMART FLOW] Clicking at cursor position...")
            if cursor_pos:
                try:
                    import pyautogui
                    pyautogui.click(cursor_pos)
                    time.sleep(0.3)
                except:
                    pass
        
        # Step 5: Type or Paste the text
        print(f"\n[SMART FLOW] Inserting text into {config['name']}...")
        
        if config['type_method'] == 'type':
            success = type_at_cursor(polished)
        else:  # paste method (safer for most apps)
            success = paste_at_cursor(polished)
        
        if success:
            return f"Smart Flow: Text inserted into {config['name']}, Sir."
        else:
            return f"Smart Flow: Text ready but paste failed. Try: {polished}"
        
    except Exception as e:
        return f"Smart Flow failed: {e}"

# ========= AI Polish =========
def polish_speech(raw_text):
    """Polish speech with AI"""
    if 'ollama_available' not in globals() or not ollama_available:
        return raw_text
    
    try:
        prompt = f"""Polish this speech like Wispr Flow:
- Remove filler words (um, uh, like, you know)
- Fix typos and grammar
- Add proper punctuation
- Keep it natural and clear:
{raw_text}"""
        
        response = ollama.chat(model=ollama_model, messages=[
            {'role': 'system', 'content': 'You are Wispr Flow AI. Polish speech to perfect text.'},
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'].strip()
    except:
        return raw_text

# ========= Load History =========
command_history = []
MAX_HISTORY = 200
HISTORY_FILE = SCRIPT_DIR / 'jarvis_history.json'

def save_history(command, response):
    entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'response': response
    }
    command_history.append(entry)
    if len(command_history) > MAX_HISTORY:
        command_history.pop(0)
    try:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except:
        pass

try:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line.strip())
                command_history.append(entry)
        command_history[:] = command_history[-MAX_HISTORY:]
        print(f"[HISTORY] Loaded {len(command_history)} entries")
except:
    pass

# ========= AI Brain =========
print("\n[AI] Initializing Ollama brain...")
ollama_available = False
ollama_model = None

try:
    import ollama
    models = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if 'phi3:mini' in models.stdout:
        ollama_model = 'phi3:mini'
    elif 'gemma4:latest' in models.stdout:
        ollama_model = 'gemma4:latest'
    
    if ollama_model:
        ollama_available = True
        print(f"[AI] OK - Using {ollama_model}")
    else:
        print(f"[AI] No models found. Run: ollama pull phi3:mini")
except:
    print(f"[AI] Ollama not running. Start with: ollama serve")

# ========= TTS =========
print("\n[TTS] Initializing...")
tts_engine = None
TTS_OK = False

if pyttsx3:
    try:
        tts_engine = pyttsx3.init()
        tts_engine.setProperty('rate', 130)
        voices = tts_engine.getProperty('voices')
        if voices:
            for v in voices:
                if 'en' in v.id.lower() and 'female' not in v.id.lower():
                    tts_engine.setProperty('voice', v.id)
                    break
        TTS_OK = True
        print("[TTS] OK - Ready")
    except Exception as e:
        print(f"[TTS] Failed: {e}")

def speak(text):
    if not tts_engine or not text:
        return
    try:
        styled = f"Sir, {text}" if not text.startswith('Sir') else text
        tts_engine.say(styled)
        tts_engine.runAndWait()
    except:
        pass

# ========= STT =========
print("\n[STT] Initializing...")
stt_model = None
STT_OK = False
mic_id = None

if faster_whisper:
    try:
        stt_model = faster_whisper.WhisperModel('tiny', device='cpu', compute_type='int8')
        STT_OK = True
        print("[STT] OK - Whisper ready")
        
        import sounddevice as sd
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                name = dev['name'].lower()
                if 'bluetooth' in name or 'headset' in name:
                    mic_id = i
                    break
        if mic_id is None:
            for i, dev in enumerate(devices):
                if dev['max_input_channels'] > 0 and dev.get('default'):
                    mic_id = i
                    break
        print(f"[STT] Mic: {mic_id}")
    except Exception as e:
        print(f"[STT] Failed: {e}")

# ========= Main Loop =========
def main():
    print("\n" + "="*60)
    print("  SMART FLOW MODE STATUS")
    print("="*60)
    print(f"  TTS: {'OK' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK' if STT_OK else 'Failed'}")
    print(f"  AI Brain: {ollama_model if ollama_available else 'Offline'}")
    print(f"  Smart Flow: Ready to detect apps and auto-paste!")
    print("="*60 + "\n")
    
    speak("JARVIS Smart Flow online. Detects apps, finds cursor, auto-pastes text, Sir.")
    
    while True:
        try:
            user_input = input("\n[You] ")
            
            if not user_input:
                continue
            
            if user_input.lower() == 'smart flow':
                result = smart_flow_mode()
                print(f"\n[JARVIS] {result}\n")
                speak(result)
            
            elif user_input.lower() in ['exit', 'quit', 'stop', 'goodbye']:
                print("\n[STOPPING...]")
                speak("Goodbye, Sir.")
                break
            
            else:
                print("\n[INFO] Try 'smart flow' to start Smart Flow Mode!")
                print("[INFO] It will detect your active app and auto-paste text at cursor!\n")
        
        except KeyboardInterrupt:
            print("\n\n[STOPPED]")
            speak("Goodbye, Sir.")
            break
        except Exception as e:
            print(f"\n[ERROR]: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
