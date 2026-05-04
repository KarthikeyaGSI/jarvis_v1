"""
JARVIS ULTIMATE AI AGENT - ALL 20 FEATURES!
Includes: Smart Flow, AI Agent Mode, Auto-Paste, App Detection
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
import traceback

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

print("\n" + "="*60)
print("  JARVIS ULTIMATE AI AGENT - ALL 20 FEATURES!")
print("="*60)
print(f"[INIT] Working from: {SCRIPT_DIR}")
print("[INIT] Loading ALL features...\n")

# ========= Auto-Import =========
def safe_import(module_name, pip_name=None):
    try:
        return __import__(module_name)
    except ImportError:
        pip_name = pip_name or module_name
        print(f"[AUTO-INSTALL] Installing {pip_name}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name, '-q'], 
                          capture_output=True, timeout=120)
            print(f"[OK] {pip_name} installed!")
            return __import__(module_name)
        except:
            print(f"[FAIL] Could not install {pip_name}")
            return None

# Import ALL libraries
pyttsx3 = safe_import('pyttsx3')
faster_whisper = safe_import('faster_whisper', 'faster-whisper')
pyautogui = safe_import('pyautogui', 'pyautogui')
psutil = safe_import('psutil', 'psutil')
tkinter = safe_import('tkinter')
keyboard_lib = safe_import('keyboard')
win32gui = safe_import('win32gui', 'pywin32')
win32process = safe_import('win32process', 'pywin32')
win32api = safe_import('win32api', 'pywin32')
pgw = safe_import('pygetwindow', 'pygetwindow')
pynput_keyboard = safe_import('pynput.keyboard', 'pynput')

# ========= Feature Flags =========
TTS_OK = False
STT_OK = False
ollama_available = False
hotkeys_available = False
window_detection_available = False

# ========= Personal Dictionary =========
PERSONAL_DICT_FILE = SCRIPT_DIR / 'jarvis_dictionary.json'
personal_dict = {}

def load_dictionary():
    global personal_dict
    try:
        if PERSONAL_DICT_FILE.exists():
            with open(PERSONAL_DICT_FILE, 'r', encoding='utf-8') as f:
                personal_dict = json.load(f)
            print(f"[DICTIONARY] Loaded {len(personal_dict)} custom words")
    except Exception as e:
        print(f"[DICTIONARY] Load error: {e}")

def save_dictionary():
    try:
        with open(PERSONAL_DICT_FILE, 'w', encoding='utf-8') as f:
            json.dump(personal_dict, f, indent=2, ensure_ascii=False)
    except:
        pass

# ========= Snippet Library =========
SNIPPET_FILE = SCRIPT_DIR / 'jarvis_snippets.json'
snippets = {}

def load_snippets():
    global snippets
    try:
        if SNIPPET_FILE.exists():
            with open(SNIPPET_FILE, 'r', encoding='utf-8') as f:
                snippets = json.load(f)
            print(f"[SNIPPETS] Loaded {len(snippets)} snippets")
    except Exception as e:
        print(f"[SNIPPETS] Load error: {e}")

def save_snippets():
    try:
        with open(SNIPPET_FILE, 'w', encoding='utf-8') as f:
            json.dump(snippets, f, indent=2, ensure_ascii=False)
    except:
        pass

# Load dictionary and snippets
load_dictionary()
load_snippets()

# ========= History Storage =========
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

# ========= Scheduled Tasks =========
scheduled_tasks = []
task_id_counter = 0
SCHEDULE_FILE = SCRIPT_DIR / 'jarvis_schedule.json'

def save_schedule():
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scheduled_tasks, f, indent=2, ensure_ascii=False)
    except:
        pass

def load_schedule():
    global task_id_counter
    try:
        if SCHEDULE_FILE.exists():
            with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
                scheduled_tasks.extend(tasks)
                if tasks:
                    task_id_counter = max(t['id'] for t in tasks) + 1
            print(f"[SCHEDULE] Loaded {len(scheduled_tasks)} scheduled tasks")
    except Exception as e:
        print(f"[SCHEDULE] Load error: {e}")

load_schedule()

# ========= AI Brain (Ollama) =========
print("\n[AI] Initializing Ollama brain...")
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

def ask_ai(prompt, system_msg='You are JARVIS. Keep responses under 30 words.'):
    if not ollama_available:
        return None
    try:
        response = ollama.chat(model=ollama_model, messages=[
            {'role': 'system', 'content': system_msg},
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'].strip()
    except:
        return None

def polish_speech(raw_text):
    """Wispr Flow: Remove fillers, fix typos, format text"""
    if not ollama_available:
        return raw_text
    
    prompt = f"""Polish this speech like Wispr Flow:
- Remove filler words (um, uh, like, you know)
- Fix typos and grammar
- Add proper punctuation and capitalization
- Keep it natural and clear:
{raw_text}"""
    
    try:
        response = ollama.chat(model=ollama_model, messages=[
            {'role': 'system', 'content': 'You polish speech to perfect text.'},
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'].strip()
    except:
        return raw_text

# ========= TTS =========
print("\n[TTS] Initializing...")
tts_engine = None

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

def listen(timeout=5):
    if not stt_model:
        return ""
    try:
        import sounddevice as sd
        import numpy as np
        
        print("\n[LISTENING... Speak now!]")
        recording = sd.rec(
            int(16000 * timeout),
            samplerate=16000,
            channels=1,
            dtype='float32',
            device=mic_id
        )
        sd.wait()
        
        segments, _ = stt_model.transcribe(recording.flatten(), language='en', vad_filter=False)
        text = " ".join(s.text for s in segments).strip()
        
        if text:
            print(f"[HEARD]: '{text}'")
        else:
            print("[NO SPEECH DETECTED]")
        
        return text
    except Exception as e:
        print(f"[STT ERROR] {e}")
        return ""

# ========= Window Detection =========
print("\n[WINDOW] Initializing window detection...")

def get_active_window_info():
    """Get active window title and process name"""
    # Try win32 first (most reliable on Windows)
    if win32gui and win32process and win32api:
        try:
            hwnd = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(hwnd)
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                process = psutil.Process(pid)
                process_name = process.name()
            except:
                process_name = "unknown"
            
            window_detection_available = True
            return {
                'title': window_title,
                'process': process_name,
                'hwnd': hwnd
            }
        except Exception as e:
            pass
    
    # Fallback: pygetwindow
    if pgw:
        try:
            win = pgw.getActiveWindow()
            if win:
                window_detection_available = True
                return {
                    'title': win.title,
                    'process': win.process if hasattr(win, 'process') else "unknown",
                    'hwnd': None
                }
        except:
            pass
    
    return {
        'title': 'unknown',
        'process': 'unknown',
        'hwnd': None
    }

def get_cursor_position():
    """Get current cursor position (x, y)"""
    if pyautogui:
        try:
            return pyautogui.position()
        except:
            pass
    return None

def type_at_cursor(text, typing_speed=0.01):
    """Type text at current cursor position"""
    if not pyautogui:
        return False
    try:
        time.sleep(0.5)
        pyautogui.write(text, interval=typing_speed)
        return True
    except Exception as e:
        print(f"[TYPE ERROR] {e}")
        return False

def paste_at_cursor(text):
    """Copy text to clipboard and paste at cursor"""
    if not tkinter:
        return False
    try:
        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        
        time.sleep(0.3)
        
        if pyautogui:
            pyautogui.hotkey('ctrl', 'v')
            return True
    except Exception as e:
        print(f"[PASTE ERROR] {e}")
        return False

# ========= App-Specific Behavior =========
APP_CONFIGS = {
    'chrome.exe': {
        'name': 'Chrome',
        'type_method': 'paste',
        'need_click': True,
    },
    'msedge.exe': {
        'name': 'Edge',
        'type_method': 'paste',
        'need_click': True,
    },
    'notepad.exe': {
        'name': 'Notepad',
        'type_method': 'type',
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
        'type_method': 'paste',
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
    if not stt_model:
        return "STT not available for Smart Flow, Sir."
    
    print(f"\n[SMART FLOW] Starting {duration}-second dictation...")
    print("[SMART FLOW] Focus the field where you want text, then speak!\n")
    
    try:
        import sounddevice as sd
        import numpy as np
        
        # Step 1: Get initial cursor position
        print("[SMART FLOW] Detecting active window and cursor position...")
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
            device=mic_id
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

def quick_flow():
    """Quick Flow: 15 second speech, polished text"""
    return smart_flow_mode(duration=15)

# ========= Hotkey Functions =========
print("\n[HOTKEYS] Initializing global shortcuts...")

def hotkey_smart_flow():
    """Ctrl+Alt+F - Start Smart Flow Mode"""
    print("\n[HOTKEY] Smart Flow Mode triggered!")
    result = smart_flow_mode()
    print(f"[HOTKEY] {result}")

def hotkey_lock_screen():
    """Ctrl+Alt+L - Lock screen"""
    print("\n[HOTKEY] Locking screen...")
    try:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        speak("Locking screen, Sir.")
    except Exception as e:
        print(f"[HOTKEY] Lock failed: {e}")

def hotkey_screenshot():
    """Ctrl+Alt+S - Take screenshot"""
    print("\n[HOTKEY] Taking screenshot...")
    if pyautogui:
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            pyautogui.screenshot(filename)
            print(f"[HOTKEY] Screenshot saved: {filename}")
            speak(f"Screenshot saved, Sir.")
        except Exception as e:
            print(f"[HOTKEY] Screenshot failed: {e}")
    else:
        print("[HOTKEY] pyautogui not installed")

def hotkey_open_chrome():
    """Ctrl+Alt+C - Open Chrome"""
    print("\n[HOTKEY] Opening Chrome...")
    try:
        subprocess.Popen('start "" "chrome"', shell=True, stdout=subprocess.PIPE)
        speak("Opening Chrome, Sir.")
    except Exception as e:
        print(f"[HOTKEY] Failed: {e}")

def hotkey_show_history():
    """Ctrl+Alt+H - Show history"""
    print("\n[HOTKEY] Showing history...")
    if not command_history:
        print("[HOTKEY] No history yet")
        return
    print("[HOTKEY] Last 5 commands:")
    for entry in command_history[-5:]:
        print(f"  {entry['timestamp']}: {entry['command']}")

def hotkey_show_shortcuts():
    """Ctrl+Alt+J - Show all shortcuts"""
    print("\n" + "="*60)
    print("  JARVIS GLOBAL SHORTCUTS")
    print("="*60)
    print("  Ctrl+Alt+J - Show this help")
    print("  Ctrl+Alt+F - Start Smart Flow Mode")
    print("  Ctrl+Alt+V - Quick voice command")
    print("  Ctrl+Alt+L - Lock screen")
    print("  Ctrl+Alt+S - Take screenshot")
    print("  Ctrl+Alt+C - Open Chrome")
    print("  Ctrl+Alt+H - Show history")
    print("="*60)
    speak("Global shortcuts listed, Sir.")

def register_hotkeys():
    """Register all global hotkeys"""
    if not keyboard_lib:
        print("[HOTKEYS] Not available - install keyboard")
        return False
    
    try:
        import keyboard as kb
        kb.add_hotkey('ctrl+alt+j', hotkey_show_shortcuts)
        kb.add_hotkey('ctrl+alt+f', hotkey_smart_flow)
        kb.add_hotkey('ctrl+alt+v', lambda: process_voice_command())
        kb.add_hotkey('ctrl+alt+l', hotkey_lock_screen)
        kb.add_hotkey('ctrl+alt+s', hotkey_screenshot)
        kb.add_hotkey('ctrl+alt+c', hotkey_open_chrome)
        kb.add_hotkey('ctrl+alt+h', hotkey_show_history)
        print("[HOTKEYS] Registered 7 global shortcuts (keyboard lib)")
        return True
            
    except Exception as e:
        print(f"[HOTKEYS] Failed to register: {e}")
        return False

# ========= Scheduling Functions =========
def add_scheduled_task(task_type, command, run_at=None, interval=None, repeat_count=None, message=""):
    global task_id_counter
    
    task = {
        'id': task_id_counter,
        'type': task_type,
        'command': command,
        'message': message,
        'created_at': datetime.now().isoformat(),
        'run_at': run_at.isoformat() if run_at else None,
        'interval': interval,
        'repeat_count': repeat_count,
        'executions': 0,
        'last_run': None,
        'active': True
    }
    
    scheduled_tasks.append(task)
    task_id_counter += 1
    save_schedule()
    
    if run_at:
        return f"Task scheduled for {run_at.strftime('%I:%M %p')}, Sir."
    elif interval:
        return f"Task will repeat every {interval} seconds, Sir."
    else:
        return f"Task added, Sir."

def list_scheduled_tasks():
    if not scheduled_tasks:
        return "No scheduled tasks, Sir."
    
    lines = ["Scheduled tasks:"]
    for t in scheduled_tasks:
        if not t['active']:
            continue
        status = ""
        if t['run_at']:
            run_time = datetime.fromisoformat(t['run_at'])
            status = f"scheduled for {run_time.strftime('%I:%M %p')}"
        elif t['interval']:
            status = f"repeats every {t['interval']}s (executed {t['executions']} times)"
        
        lines.append(f"  [{t['id']}] {t['command']} - {status}")
    
    return "\n".join(lines)

def remove_scheduled_task(task_id):
    for task in scheduled_tasks:
        if task['id'] == task_id:
            task['active'] = False
            save_schedule()
            return f"Task {task_id} removed, Sir."
    return f"Task {task_id} not found, Sir."

def execute_scheduled_task(task):
    try:
        if task['type'] == 'reminder':
            msg = task['message'] or task['command']
            speak(f"Reminder: {msg}")
            return f"Reminder: {msg}"
        
        elif task['type'] in ['command', 'recurring']:
            result = process_command(task['command'])
            return result
        
    except Exception as e:
        return f"Task execution failed: {e}"
    finally:
        task['last_run'] = datetime.now().isoformat()
        task['executions'] += 1
        
        if task['type'] == 'command' or (task['repeat_count'] and task['executions'] >= task['repeat_count']):
            task['active'] = False
        
        save_schedule()

def scheduler_loop():
    while True:
        try:
            now = datetime.now()
            
            for task in scheduled_tasks:
                if not task['active']:
                    continue
                
                if task['run_at']:
                    run_time = datetime.fromisoformat(task['run_at'])
                    if now >= run_time:
                        result = execute_scheduled_task(task)
                        print(f"[SCHEDULER] Executed task {task['id']}: {result}")
                
                elif task['interval']:
                    if task['last_run']:
                        last_run = datetime.fromisoformat(task['last_run'])
                        if (now - last_run).total_seconds() >= task['interval']:
                            result = execute_scheduled_task(task)
                            print(f"[SCHEDULER] Executed recurring task {task['id']}: {result}")
                    else:
                        result = execute_scheduled_task(task)
                        print(f"[SCHEDULER] Executed recurring task {task['id']}: {result}")
            
            # Clean up inactive tasks
            scheduled_tasks[:] = [t for t in scheduled_tasks if t['active']]
            save_schedule()
            
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
        
        time.sleep(1)

# Start scheduler thread
scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()
print("[SCHEDULER] Started background scheduler")

# ========= PC CONTROL FUNCTIONS =========
def open_app(name):
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
        'explorer': 'explorer', 'word': 'winword', 'spotify': 'spotify',
    }
    exe = app_map.get(name.lower(), name.lower())
    try:
        subprocess.Popen(f'start "" "{exe}"', shell=True, stdout=subprocess.PIPE)
        return f"Opening {name}, Sir."
    except:
        try:
            subprocess.Popen(f'start "" "{exe}.exe"', shell=True)
            return f"Opening {name}, Sir."
        except Exception as e:
            return f"Failed to open {name}: {e}"

def search_web(query):
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}, Sir."
    except Exception as e:
        return f"Search failed: {e}"

def take_screenshot():
    if not pyautogui:
        return "pyautogui not installed. Run: pip install pyautogui"
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(filename)
        return f"Screenshot saved as {filename}, Sir."
    except Exception as e:
        return f"Screenshot failed: {e}"

def lock_screen():
    try:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        return "Locking screen, Sir."
    except Exception as e:
        return f"Failed: {e}"

def get_battery():
    if not psutil:
        return "psutil not installed. Run: pip install psutil"
    try:
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery: {battery.percent}% ({'plugged in' if battery.power_plugged else 'on battery'}), Sir."
        return "No battery detected, Sir."
    except Exception as e:
        return f"Failed: {e}"

def get_cpu():
    if not psutil:
        return "psutil not installed."
    try:
        cpu = psutil.cpu_percent(interval=1)
        return f"CPU usage: {cpu}%, Sir."
    except Exception as e:
        return f"Failed: {e}"

def get_ram():
    if not psutil:
        return "psutil not installed."
    try:
        ram = psutil.virtual_memory()
        used = ram.used // (1024**3)
        total = ram.total // (1024**3)
        return f"RAM: {used}GB / {total}GB ({ram.percent}%), Sir."
    except Exception as e:
        return f"Failed: {e}"

def type_text(text):
    if not pyautogui:
        return "pyautogui not installed."
    try:
        time.sleep(2)
        pyautogui.write(text)
        return f"Typed: {text}, Sir."
    except Exception as e:
        return f"Failed: {e}"

def get_clipboard():
    if not tkinter:
        return "tkinter not available."
    try:
        root = tkinter.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        return f"Clipboard: {content[:100]}..., Sir." if content else "Clipboard empty, Sir."
    except Exception as e:
        return f"Failed: {e}"

def create_file(name, content=""):
    try:
        with open(name, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created file {name}, Sir."
    except Exception as e:
        return f"Failed: {e}"

def create_folder(name):
    try:
        os.makedirs(name, exist_ok=True)
        return f"Created folder {name}, Sir."
    except Exception as e:
        return f"Failed: {e}"

def delete_file(name):
    try:
        path = Path(name)
        if path.is_file():
            path.unlink()
            return f"Deleted {name}, Sir."
        elif path.is_dir():
            import shutil
            shutil.rmtree(path)
            return f"Deleted folder {name}, Sir."
        return f"{name} not found, Sir."
    except Exception as e:
        return f"Failed: {e}"

def control_volume(action):
    try:
        if action == 'up':
            os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]175)")
            return "Volume increased, Sir."
        elif action == 'down':
            os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]174)")
            return "Volume decreased, Sir."
        elif action == 'mute':
            os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]173)")
            return "Volume muted, Sir."
    except Exception as e:
        return f"Failed: {e}"

def parse_time(text):
    """Parse time from text"""
    text_lower = text.lower()
    now = datetime.now()
    
    # "in X minutes/hours"
    if 'in ' in text_lower:
        try:
            parts = text_lower.split('in ')[-1].split()
            amount = int(parts[0])
            unit = parts[1] if len(parts) > 1 else 'minutes'
            
            if 'minute' in unit:
                return now + timedelta(minutes=amount)
            elif 'hour' in unit:
                return now + timedelta(hours=amount)
            elif 'second' in unit:
                return now + timedelta(seconds=amount)
        except:
            pass
    
    # "at HH:MM"
    if 'at ' in text_lower:
        try:
            time_str = text_lower.split('at ')[-1].strip()
            time_obj = datetime.strptime(time_str, '%H:%M').time()
            run_at = datetime.combine(now.date(), time_obj)
            if run_at < now:
                run_at += timedelta(days=1)
            return run_at
        except:
            pass
    
    # "every X minutes/hours"
    if 'every ' in text_lower:
        try:
            parts = text_lower.split('every ')[-1].split()
            amount = int(parts[0])
            unit = parts[1] if len(parts) > 1 else 'minutes'
            
            if 'minute' in unit:
                return timedelta(minutes=amount)
            elif 'hour' in unit:
                return timedelta(hours=amount)
            elif 'second' in unit:
                return timedelta(seconds=amount)
        except:
            pass
    
    return None

# ========= COMMAND PROCESSING =========
def process_voice_command():
    """Quick voice command via hotkey"""
    text = listen(timeout=5)
    if text:
        print(f"\n[HOTKEY] Processing: {text}")
        result = process_command(text)
        print(f"[HOTKEY] Result: {result}")
        speak(result)

def process_command(text):
    """Process ANY command - AI Agent Mode"""
    if not text:
        return "No input, Sir."
    
    text_lower = text.lower()
    
    # Exit
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return "STOP"
    
    # Help
    if 'help' in text_lower:
        return """JARVIS ULTIMATE - ALL 20 FEATURES:

SYSTEM: Lock screen, Sleep, Shutdown, Restart, System info
APPS: Open [app], Search for [query]
FILES: Create/open/delete files & folders
MEDIA: Volume up/down/mute, Screenshot
INPUT: Type [text], Clipboard, Click
WISPR FLOW: flow mode, quick flow
SMART FLOW: smart flow (auto-paste to apps!)
SCHEDULE: Remind me, Run at, Repeat every
AI: Ask me anything! (Ollama powered)
TIME: What time/date is it?
DICT: add word [X], show dictionary
SNIP: add snippet [cue] = [text]
HOTKEYS: Ctrl+Alt+J, Ctrl+Alt+F, etc.
UTILS: Battery, CPU, RAM, History"""

    # Dictionary management
    if 'add word ' in text_lower:
        word = text.split('add word ')[-1].strip()
        personal_dict[word.lower()] = {
            'word': word,
            'added_at': datetime.now().isoformat()
        }
        save_dictionary()
        return f"Added '{word}' to dictionary, Sir."

    if 'show dictionary' in text_lower:
        if not personal_dict:
            return "Dictionary is empty, Sir."
        words = [v['word'] for v in personal_dict.values()]
        return f"Dictionary words: {' ,'.join(words[:10])}"

    # Snippet management
    if 'add snippet ' in text_lower:
        try:
            parts = text.split('add snippet ')[-1].split(' = ')
            cue = parts[0].strip()
            full_text = parts[1].strip()
            snippets[cue.lower()] = {
                'cue': cue,
                'text': full_text,
                'created_at': datetime.now().isoformat()
            }
            save_snippets()
            return f"Snippet '{cue}' saved, Sir."
        except:
            return "Use: add snippet [cue] = [full text], Sir."

    if 'show snippets' in text_lower:
        if not snippets:
            return "No snippets saved, Sir."
        cues = [v['cue'] for v in snippets.values()]
        return f"Snippets: {' ,'.join(cues[:10])}"

    # Expand snippets in text
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in snippets:
            words[i] = snippets[word.lower()]['text']
    text = ' '.join(words)

    # Smart Flow Mode
    if 'smart flow' in text_lower or 'start smart flow' in text_lower:
        result = smart_flow_mode()
        save_history(text, result)
        return result

    if 'quick flow' in text_lower or 'fast flow' in text_lower:
        result = quick_flow()
        save_history(text, result)
        return result

    # Flow Mode (basic)
    if 'flow mode' in text_lower or 'start flow' in text_lower:
        if not stt_model:
            return "STT not available, Sir."
        result = "Use 'smart flow' for auto-paste to apps, Sir."
        save_history(text, result)
        return result

    # History
    if 'history' in text_lower:
        if not command_history:
            return "No history yet, Sir."
        lines = [f"{h['timestamp']}: {h['command']} -> {h['response'][:50]}..." 
                  for h in command_history[-10:]]
        return "Last 10 commands:\n" + "\n".join(lines)

    if 'time' in text_lower:
        return f"The time is {datetime.now().strftime('%I:%M %p')}, Sir."

    if 'day' in text_lower or 'date' in text_lower:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, Sir."

    # Scheduling
    if 'remind me' in text_lower or 'set reminder' in text_lower:
        run_at = parse_time(text)
        if not run_at:
            return "Please specify time like 'in 5 minutes' or 'at 14:30', Sir."
        
        msg = text
        for prefix in ['remind me to ', 'remind me in ', 'remind me at ', 'set reminder to ']:
            if prefix in text_lower:
                msg = text.split(prefix)[-1].strip()
                for time_word in ['in ', 'at ']:
                    if time_word in msg.lower():
                        msg = msg.split(time_word)[0].strip()
                break
        
        result = add_scheduled_task('reminder', msg, run_at=run_at, message=msg)
        save_history(text, result)
        return result

    if text_lower.startswith('run ') and (' at ' in text_lower or ' in ' in text_lower):
        parts = text.split()
        time_keywords = ['at', 'in', 'every']
        
        command_parts = []
        for i, word in enumerate(parts):
            if word.lower() in time_keywords and i > 1:
                command_parts = parts[1:i]
                break
        
        if not command_parts:
            command_parts = parts[1:]
        
        command = ' '.join(command_parts)
        
        if 'every ' in text_lower:
            interval = parse_time(text)
            if interval and isinstance(interval, timedelta):
                result = add_scheduled_task('recurring', command, interval=interval.total_seconds())
                save_history(text, result)
                return result
        else:
            run_at = parse_time(text)
            if run_at and isinstance(run_at, datetime):
                result = add_scheduled_task('command', command, run_at=run_at)
                save_history(text, result)
                return result
        
        return "Please specify time like 'in 5 minutes', 'at 14:30', or 'every hour', Sir."

    if 'list scheduled' in text_lower or 'show scheduled' in text_lower:
        return list_scheduled_tasks()

    if 'remove task ' in text_lower or 'delete task ' in text_lower:
        try:
            task_id = int(text.split('task ')[-1].strip())
            result = remove_scheduled_task(task_id)
            save_history(text, result)
            return result
        except:
            return "Please specify task ID, Sir."

    # System commands
    if any(p in text_lower for p in ['lock screen', 'lock pc']):
        result = lock_screen()
        save_history(text, result)
        return result

    # Media
    if 'volume up' in text_lower:
        result = control_volume('up')
        save_history(text, result)
        return result

    if 'volume down' in text_lower:
        result = control_volume('down')
        save_history(text, result)
        return result

    if 'mute' in text_lower:
        result = control_volume('mute')
        save_history(text, result)
        return result

    # Screen
    if 'screenshot' in text_lower:
        result = take_screenshot()
        save_history(text, result)
        return result

    # Input
    if text_lower.startswith('type '):
        msg = text.split('type ', 1)[-1].strip()
        result = type_text(msg)
        save_history(text, result)
        return result

    if 'clipboard' in text_lower:
        result = get_clipboard()
        save_history(text, result)
        return result

    # System Info
    if 'battery' in text_lower:
        return get_battery()

    if 'cpu' in text_lower and 'usage' in text_lower:
        return get_cpu()

    if 'ram' in text_lower or 'memory' in text_lower:
        return get_ram()

    # Files
    if text_lower.startswith('create file '):
        name = text.split('create file ')[-1].strip()
        result = create_file(name)
        save_history(text, result)
        return result

    if text_lower.startswith('create folder '):
        name = text.split('create folder ')[-1].strip()
        result = create_folder(name)
        save_history(text, result)
        return result

    if text_lower.startswith('delete '):
        name = text.split('delete ')[-1].strip()
        result = delete_file(name)
        save_history(text, result)
        return result

    # Apps
    for trigger in ['open ', 'launch ']:
        if trigger in text_lower:
            app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
            if app:
                result = open_app(app)
                save_history(text, result)
                return result

    if 'search for ' in text_lower:
        query = text_lower.split('search for ')[-1].strip()
        if query:
            result = search_web(query)
            save_history(text, result)
            return result

    # AI Fallback - FULL AI AGENT MODE
    if ollama_available:
        ai_response = ask_ai(text, system_msg='You are JARVIS, a helpful AI assistant. Execute the user\'s request or provide information.')
        if ai_response:
            save_history(text, ai_response)
            return f"{ai_response}, Sir."

    result = "Sorry, I didn't understand. Say 'Help' for all 20 features, Sir."
    save_history(text, result)
    return result

# ========= MAIN LOOP =========
def main():
    print("\n" + "="*60)
    print("  ULTIMATE AI AGENT STATUS")
    print("="*60)
    print(f"  TTS: {'OK' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK' if STT_OK else 'Failed'}")
    print(f"  AI Brain: {ollama_model if ollama_available else 'Offline'}")
    print(f"  Hotkeys: {'OK' if keyboard_lib else 'Failed (install keyboard)'}")
    print(f"  Window Detection: {'OK' if window_detection_available else 'Failed'}")
    print(f"  Smart Flow: {'OK' if pyautogui and window_detection_available else 'Needs pyautogui/pywin32'}")
    print(f"  Scheduler: {len(scheduled_tasks)} tasks")
    print(f"  History: {len(command_history)} entries")
    print(f"  Dictionary: {len(personal_dict)} words")
    print(f"  Snippets: {len(snippets)} saved")
    print("="*60)
    print("\n  ALL 20 FEATURES READY!")
    print("="*60 + "\n")
    
    # Register hotkeys
    if keyboard_lib:
        hotkeys_available = register_hotkeys()
        if hotkeys_available:
            print("\n[INFO] Global hotkeys active! Press Ctrl+Alt+J for help")
    
    speak("JARVIS Ultimate AI Agent online. All 20 features ready, Sir.")
    
    mode = 'text'
    
    while True:
        try:
            if mode == 'text':
                try:
                    user_input = input("\n[You] ")
                except EOFError:
                    break
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'voice':
                    mode = 'voice'
                    print("\n[SWITCHED TO VOICE MODE]")
                    speak("Voice mode activated.")
                    continue
                
                if user_input.lower() == 'text':
                    mode = 'text'
                    print("\n[SWITCHED TO TEXT MODE]")
                    continue
                
                print(f"\n[PROCESSING...]")
                result = process_command(user_input)
                
                if result == "STOP":
                    print("\n[STOPPING...]")
                    speak("Goodbye, Sir.")
                    break
                
                print(f"[JARVIS] {result}\n")
                speak(result)
            
            else:  # voice mode
                text = listen()
                if text:
                    print(f"\n[PROCESSING...]")
                    result = process_command(text)
                    
                    if result == "STOP":
                        print("\n[STOPPING...]")
                        speak("Goodbye, Sir.")
                        break
                    
                    print(f"[JARVIS] {result}\n")
                    speak(result)
                    
                    if 'text' in text.lower():
                        mode = 'text'
                        print("\n[SWITCHED TO TEXT MODE]")
                        continue
        
        except KeyboardInterrupt:
            print("\n\n[STOPPED]")
            speak("Goodbye, Sir.")
            break
        except Exception as e:
            print(f"\n[ERROR]: {e}")
            traceback.print_exc()
            time.sleep(1)

if __name__ == "__main__":
    main()
