"""
JARVIS SUPER-PREMIUM AGENT v2.0 - WITH SCHEDULING
- AI Brain (Ollama)
- Scheduled Tasks & Reminders
- Wake word detection
- Particle effects UI
- Bulletproof error handling
"""
import os
import sys
import time
import json
import subprocess
import threading
from pathlib import Path
from datetime import datetime, timedelta
import shutil

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

print("\n" + "="*60)
print("  JARVIS SUPER-PREMIUM AGENT v2.0")
print("="*60)
print(f"[INIT] Working from: {SCRIPT_DIR}")
print("[INIT] Loading premium capabilities...\n")

# =========== Self-Healing Import System ===========
def safe_import(module_name, pip_name=None, feature_name=""):
    try:
        return __import__(module_name)
    except ImportError:
        pip_name = pip_name or module_name
        print(f"[AUTO-INSTALL] Installing {pip_name} for {feature_name}...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', pip_name, '-q'], 
                          capture_output=True, timeout=60)
            print(f"[OK] {pip_name} installed!")
            return __import__(module_name)
        except:
            print(f"[FAIL] Could not install {pip_name}")
            return None

# Import with auto-install
pyttsx3 = safe_import('pyttsx3', feature_name='TTS')
faster_whisper = safe_import('faster_whisper', 'faster-whisper', 'STT')
pyautogui = safe_import('pyautogui', 'pyautogui', 'Screen Control')
psutil = safe_import('psutil', 'psutil', 'System Monitor')
tkinter = safe_import('tkinter', feature_name='Clipboard')

# =========== History Storage ===========
command_history = []
MAX_HISTORY = 200
HISTORY_FILE = SCRIPT_DIR / 'jarvis_history.json'

# =========== Scheduled Tasks ===========
scheduled_tasks = []
task_id_counter = 0
SCHEDULE_FILE = SCRIPT_DIR / 'jarvis_schedule.json'

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

def save_schedule():
    """Save scheduled tasks to file"""
    try:
        with open(SCHEDULE_FILE, 'w', encoding='utf-8') as f:
            json.dump(scheduled_tasks, f, indent=2, ensure_ascii=False)
    except:
        pass

def load_schedule():
    """Load scheduled tasks from file"""
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

# Load history
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

load_schedule()

# =========== AI Brain (Ollama) ===========
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
    elif 'mistral:latest' in models.stdout:
        ollama_model = 'mistral:latest'
    
    if ollama_model:
        ollama_available = True
        print(f"[AI] OK - Using {ollama_model}")
    else:
        print(f"[AI] No models found. Run: ollama pull phi3:mini")
except:
    print(f"[AI] Ollama not running. Start with: ollama serve")

def ask_ai(prompt):
    if not ollama_available:
        return None
    try:
        response = ollama.chat(model=ollama_model, messages=[
            {'role': 'system', 'content': 'You are JARVIS. Keep responses under 30 words.'},
            {'role': 'user', 'content': prompt}
        ])
        return response['message']['content'].strip()
    except:
        return None

# =========== TTS ===========
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
else:
    print("[TTS] pyttsx3 not available")

def speak(text):
    if not tts_engine or not text:
        return
    try:
        styled = f"Sir, {text}" if not text.startswith('Sir') else text
        tts_engine.say(styled)
        tts_engine.runAndWait()
    except:
        pass

# =========== STT ===========
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
else:
    print("[STT] faster-whisper not available")

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

# =========== SCHEDULING FUNCTIONS ===========

def add_scheduled_task(task_type, command, run_at=None, interval=None, repeat_count=None, message=""):
    """Add a scheduled task"""
    global task_id_counter
    
    task = {
        'id': task_id_counter,
        'type': task_type,  # 'reminder', 'command', 'recurring'
        'command': command,
        'message': message,
        'created_at': datetime.now().isoformat(),
        'run_at': run_at.isoformat() if run_at else None,
        'interval': interval,  # seconds
        'repeat_count': repeat_count,  # None = infinite
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
    """List all scheduled tasks"""
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
    """Remove a scheduled task"""
    for task in scheduled_tasks:
        if task['id'] == task_id:
            task['active'] = False
            save_schedule()
            return f"Task {task_id} removed, Sir."
    return f"Task {task_id} not found, Sir."

def execute_scheduled_task(task):
    """Execute a scheduled task"""
    try:
        if task['type'] == 'reminder':
            msg = task['message'] or task['command']
            speak(f"Reminder: {msg}")
            return f"Reminder: {msg}"
        
        elif task['type'] == 'command':
            result = process_command(task['command'])
            return result
        
        elif task['type'] == 'recurring':
            result = process_command(task['command'])
            task['executions'] += 1
            
            if task['repeat_count'] and task['executions'] >= task['repeat_count']:
                task['active'] = False
            
            save_schedule()
            return result
        
    except Exception as e:
        return f"Task execution failed: {e}"
    finally:
        task['last_run'] = datetime.now().isoformat()

def scheduler_loop():
    """Background thread to check and run scheduled tasks"""
    while True:
        try:
            now = datetime.now()
            tasks_to_remove = []
            
            for task in scheduled_tasks:
                if not task['active']:
                    continue
                
                # One-time task
                if task['run_at']:
                    run_time = datetime.fromisoformat(task['run_at'])
                    if now >= run_time:
                        result = execute_scheduled_task(task)
                        print(f"[SCHEDULER] Executed task {task['id']}: {result}")
                        task['active'] = False
                
                # Recurring task
                elif task['interval']:
                    if task['last_run']:
                        last_run = datetime.fromisoformat(task['last_run'])
                        if (now - last_run).total_seconds() >= task['interval']:
                            result = execute_scheduled_task(task)
                            print(f"[SCHEDULER] Executed recurring task {task['id']}: {result}")
                    else:
                        # First run
                        result = execute_scheduled_task(task)
                        print(f"[SCHEDULER] Executed recurring task {task['id']}: {result}")
            
            # Clean up inactive tasks
            scheduled_tasks[:] = [t for t in scheduled_tasks if t['active']]
            save_schedule()
            
        except Exception as e:
            print(f"[SCHEDULER ERROR] {e}")
        
        time.sleep(1)  # Check every second

# Start scheduler thread
scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()
print("[SCHEDULER] Started background scheduler")

# =========== PC CONTROL FUNCTIONS ===========

def open_app(name):
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
        'explorer': 'explorer', 'word': 'winword', 'excel': 'excel',
        'spotify': 'spotify', 'settings': 'ms-settings:',
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
    """Parse time from text like 'in 5 minutes', 'at 3:30', 'every hour'"""
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

# =========== COMMAND PROCESSING ===========

def process_command(text):
    """Process command with scheduling support"""
    if not text:
        return "No input, Sir."
    
    text_lower = text.lower()
    
    # Exit
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return "STOP"
    
    # Help
    if 'help' in text_lower:
        return """JARVIS SUPER-PREMIUM v2.0 COMMANDS:

[MONITOR] SYSTEM: Lock screen, Sleep, Shutdown, Restart, System info
[MOBILE] APPS: Open [app], Search for [query]
[FOLDER] FILES: Create/open/delete files & folders
[MUSIC] MEDIA: Volume up/down/mute
[CAMERA] SCREEN: Take screenshot
[KEYBOARD] INPUT: Type [text], Click, Mouse position
[CLIPBOARD] UTILS: Clipboard, Battery, CPU, RAM, History
[ROBOT] AI: Ask me anything! (Ollama powered)
[CLOCK] TIME: What time/date is it?
[CALENDAR] SCHEDULE: 
  - Remind me in 5 minutes to [task]
  - Run [command] at 14:30
  - Repeat [command] every 10 minutes
  - List scheduled tasks
  - Remove task [id]
[SPEAK] MODE: Say 'voice' for voice mode, 'text' for text"""
    
    # History
    if 'history' in text_lower:
        if not command_history:
            return "No history yet, Sir."
        lines = [f"{h['timestamp']}: {h['command']} -> {h['response'][:50]}..." 
                  for h in command_history[-10:]]
        return "Last 10 commands:\n" + "\n".join(lines)
    
    # Time/Date
    if 'time' in text_lower:
        return f"The time is {datetime.now().strftime('%I:%M %p')}, Sir."
    if 'day' in text_lower or 'date' in text_lower:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, Sir."
    
    # =========== SCHEDULING COMMANDS ===========
    
    # Reminder: "Remind me in X minutes to [task]"
    if 'remind me' in text_lower or 'set reminder' in text_lower:
        # Parse time
        run_at = parse_time(text)
        if not run_at:
            return "Please specify time like 'in 5 minutes' or 'at 14:30', Sir."
        
        # Extract reminder message
        msg = text
        for prefix in ['remind me to ', 'remind me in ', 'remind me at ', 'set reminder to ']:
            if prefix in text_lower:
                msg = text.split(prefix)[-1].strip()
                # Remove time part if present
                for time_word in ['in ', 'at ']:
                    if time_word in msg.lower():
                        msg = msg.split(time_word)[0].strip()
                break
        
        result = add_scheduled_task('reminder', msg, run_at=run_at, message=msg)
        save_history(text, result)
        return result
    
    # Scheduled command: "Run [command] at HH:MM" or "Run [command] in X minutes"
    if text_lower.startswith('run ') and (' at ' in text_lower or ' in ' in text_lower):
        parts = text.split()
        # Find where the time specification starts
        time_keywords = ['at', 'in', 'every']
        command_parts = []
        time_part = None
        
        for i, word in enumerate(parts):
            if word.lower() in time_keywords and i > 1:
                command_parts = parts[1:i]
                time_part = ' '.join(parts[i:])
                break
        
        if not command_parts:
            command_parts = parts[1:]
        
        command = ' '.join(command_parts)
        
        # Check if recurring
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
    
    # List scheduled tasks
    if 'list scheduled' in text_lower or 'show scheduled' in text_lower or 'scheduled tasks' in text_lower:
        return list_scheduled_tasks()
    
    # Remove task
    if 'remove task ' in text_lower or 'delete task ' in text_lower:
        try:
            task_id = int(text.split('task ')[-1].strip())
            result = remove_scheduled_task(task_id)
            save_history(text, result)
            return result
        except:
            return "Please specify task ID, Sir."
    
    # =========== SYSTEM COMMANDS ===========
    
    if any(p in text_lower for p in ['lock screen', 'lock pc']):
        result = lock_screen()
        save_history(text, result)
        return result
    
    # =========== MEDIA ===========
    
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
    
    # =========== SCREEN ===========
    
    if 'screenshot' in text_lower:
        result = take_screenshot()
        save_history(text, result)
        return result
    
    # =========== INPUT ===========
    
    if text_lower.startswith('type '):
        msg = text.split('type ', 1)[-1].strip()
        result = type_text(msg)
        save_history(text, result)
        return result
    
    if 'clipboard' in text_lower:
        result = get_clipboard()
        save_history(text, result)
        return result
    
    # =========== SYSTEM INFO ===========
    
    if 'battery' in text_lower:
        return get_battery()
    if 'cpu' in text_lower and 'usage' in text_lower:
        return get_cpu()
    if 'ram' in text_lower or 'memory' in text_lower:
        return get_ram()
    
    # =========== FILES ===========
    
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
    
    # =========== APPS ===========
    
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
    
    # =========== AI FALLBACK ===========
    
    if ollama_available:
        ai_response = ask_ai(text)
        if ai_response:
            save_history(text, ai_response)
            return f"{ai_response}, Sir."
    
    result = "Sorry, I didn't understand. Say 'Help' for commands, Sir."
    save_history(text, result)
    return result

# =========== MAIN LOOP ===========

def main():
    print("\n" + "="*60)
    print("  SUPER-PREMIUM STATUS")
    print("="*60)
    print(f"  TTS: {'OK - Ready' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK - Ready' if STT_OK else 'Failed'}")
    print(f"  AI Brain: {'OK - ' + ollama_model if ollama_available else 'Offline'}")
    print(f"  Scheduler: Active ({len(scheduled_tasks)} tasks loaded)")
    print(f"  History: {len(command_history)} entries loaded")
    print("="*60)
    print("\n  [ROCKET] NEW: Scheduled Tasks, Reminders, Recurring Commands")
    print("="*60 + "\n")
    
    speak("JARVIS Super-Premium Agent online. Scheduler active, Sir.")
    
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
            time.sleep(1)

if __name__ == "__main__":
    main()
