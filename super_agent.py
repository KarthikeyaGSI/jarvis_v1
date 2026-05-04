"""
JARVIS SUPER AGENT - Full PC Control
Can do ANY task you say: files, apps, system, media, automation
NO admin required for most tasks
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime
import shutil

# Get script directory
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

print("\n" + "="*60)
print("  JARVIS SUPER AGENT - Full PC Control")
print("="*60)
print(f"\n[INIT] Working from: {SCRIPT_DIR}")
print("[INIT] Loading super-agent capabilities...\n")

# =========== History Storage ===========
command_history = []
MAX_HISTORY = 100
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

# =========== TTS ===========
print("[TTS] Initializing...")
tts_engine = None
TTS_OK = False

try:
    import pyttsx3
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

# =========== STT ===========
print("\n[STT] Initializing...")
stt_model = None
STT_OK = False
mic_id = None

try:
    from faster_whisper import WhisperModel
    stt_model = WhisperModel('tiny', device='cpu', compute_type='int8')
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

# =========== PC CONTROL FUNCTIONS ===========

def open_app(name):
    """Open any application"""
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
        'explorer': 'explorer', 'file explorer': 'explorer',
        'word': 'winword', 'excel': 'excel', 'powerpoint': 'powerpnt',
        'spotify': 'spotify', 'music': 'spotify',
        'settings': 'ms-settings:', 'task manager': 'taskmgr',
    }
    exe = app_map.get(name.lower(), name.lower())
    try:
        subprocess.Popen(f'start "" "{exe}"', shell=True, 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return f"Opening {name}, Sir."
    except:
        try:
            subprocess.Popen(f'start "" "{exe}.exe"', shell=True)
            return f"Opening {name}, Sir."
        except Exception as e:
            return f"Failed to open {name}: {e}"

def search_web(query):
    """Search web"""
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}, Sir."
    except Exception as e:
        return f"Search failed: {e}"

def create_file(name, content=""):
    """Create a file"""
    try:
        with open(name, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Created file {name}, Sir."
    except Exception as e:
        return f"Failed to create file: {e}"

def create_folder(name):
    """Create a folder"""
    try:
        os.makedirs(name, exist_ok=True)
        return f"Created folder {name}, Sir."
    except Exception as e:
        return f"Failed to create folder: {e}"

def delete_file(name):
    """Delete a file or folder"""
    try:
        path = Path(name)
        if path.is_file():
            path.unlink()
            return f"Deleted file {name}, Sir."
        elif path.is_dir():
            shutil.rmtree(path)
            return f"Deleted folder {name}, Sir."
        else:
            return f"{name} not found, Sir."
    except Exception as e:
        return f"Failed to delete: {e}"

def list_files(path="."):
    """List files in a directory"""
    try:
        files = list(Path(path).iterdir())
        if not files:
            return f"Directory {path} is empty, Sir."
        names = [f.name for f in files[:10]]
        return f"Files in {path}: {', '.join(names)}"
    except Exception as e:
        return f"Failed to list files: {e}"

def take_screenshot():
    """Take a screenshot"""
    try:
        import pyautogui
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(filename)
        return f"Screenshot saved as {filename}, Sir."
    except ImportError:
        return "pyautogui not installed. Install with: pip install pyautogui"
    except Exception as e:
        return f"Screenshot failed: {e}"

def control_volume(action):
    """Control system volume"""
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
        return f"Volume control failed: {e}"

def lock_screen():
    """Lock the screen"""
    try:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        return "Locking screen, Sir."
    except Exception as e:
        return f"Failed to lock screen: {e}"

def sleep_pc():
    """Put PC to sleep"""
    try:
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        return "Putting PC to sleep, Sir."
    except Exception as e:
        return f"Failed to sleep: {e}"

def shutdown_pc(delay=0):
    """Shutdown PC with optional delay"""
    try:
        if delay > 0:
            subprocess.Popen(f'shutdown /s /t {delay}', shell=True)
            return f"Shutting down in {delay} seconds, Sir."
        else:
            subprocess.Popen('shutdown /s /t 0', shell=True)
            return "Shutting down now, Sir."
    except Exception as e:
        return f"Shutdown failed: {e}"

def restart_pc(delay=0):
    """Restart PC with optional delay"""
    try:
        if delay > 0:
            subprocess.Popen(f'shutdown /r /t {delay}', shell=True)
            return f"Restarting in {delay} seconds, Sir."
    except Exception as e:
        return f"Restart failed: {e}"

def cancel_shutdown():
    """Cancel pending shutdown"""
    try:
        subprocess.Popen('shutdown /a', shell=True)
        return "Shutdown cancelled, Sir."
    except Exception as e:
        return f"Cancel failed: {e}"

def get_clipboard():
    """Get clipboard content"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        return f"Clipboard: {content[:100]}..., Sir." if content else "Clipboard is empty, Sir."
    except Exception as e:
        return f"Failed to read clipboard: {e}"

def set_clipboard(text):
    """Set clipboard content"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.destroy()
        return f"Copied to clipboard, Sir."
    except Exception as e:
        return f"Failed to set clipboard: {e}"

def type_text(text):
    """Type text at cursor"""
    try:
        import pyautogui
        time.sleep(2)  # Give user time to focus input
        pyautogui.write(text)
        return f"Typed: {text}, Sir."
    except ImportError:
        return "pyautogui not installed. Install with: pip install pyautogui"
    except Exception as e:
        return f"Type failed: {e}"

def press_key(key):
    """Press a keyboard key"""
    try:
        import pyautogui
        pyautogui.press(key)
        return f"Pressed {key}, Sir."
    except ImportError:
        return "pyautogui not installed."
    except Exception as e:
        return f"Key press failed: {e}"

def click(x=None, y=None):
    """Click at position or current position"""
    try:
        import pyautogui
        if x is not None and y is not None:
            pyautogui.click(x, y)
            return f"Clicked at {x}, {y}, Sir."
        else:
            pyautogui.click()
            return "Clicked, Sir."
    except ImportError:
        return "pyautogui not installed."
    except Exception as e:
        return f"Click failed: {e}"

def get_mouse_position():
    """Get current mouse position"""
    try:
        import pyautogui
        x, y = pyautogui.position()
        return f"Mouse position: {x}, {y}, Sir."
    except ImportError:
        return "pyautogui not installed."
    except Exception as e:
        return f"Failed: {e}"

def minimize_all():
    """Minimize all windows (show desktop)"""
    try:
        os.system('powershell -Command (New-Object -ComObject WScript.Shell).SendKeys("^d")')
        return "Minimized all windows, Sir."
    except Exception as e:
        return f"Failed: {e}"

def open_folder(path=None):
    """Open a folder in explorer"""
    try:
        if path is None:
            path = os.getcwd()
        subprocess.Popen(f'explorer "{path}"')
        return f"Opened folder {path}, Sir."
    except Exception as e:
        return f"Failed to open folder: {e}"

def run_command(cmd):
    """Run a safe command"""
    blocked = ['format', 'del /f /q', 'rm -rf', 'shutdown /s /t 0']
    if any(b in cmd.lower() for b in blocked):
        return "Command blocked for safety, Sir."
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout[:200] if result.stdout else "Command executed."
        return f"{output}, Sir."
    except Exception as e:
        return f"Command failed: {e}"

def get_system_info():
    """Get system information"""
    try:
        import platform
        info = {
            'OS': platform.system() + ' ' + platform.release(),
            'Version': platform.version(),
            'Machine': platform.machine(),
            'Processor': platform.processor()[:50],
            'Python': platform.python_version()
        }
        lines = [f"{k}: {v}" for k, v in info.items()]
        return "System Info:\n" + "\n".join(lines) + ", Sir."
    except Exception as e:
        return f"Failed to get system info: {e}"

def get_battery():
    """Get battery status"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            plugged = "plugged in" if battery.power_plugged else "on battery"
            return f"Battery: {percent}% ({plugged}), Sir."
        return "No battery detected, Sir."
    except ImportError:
        return "psutil not installed. Install with: pip install psutil"
    except Exception as e:
        return f"Failed: {e}"

def get_cpu_usage():
    """Get CPU usage"""
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        return f"CPU usage: {cpu}%, Sir."
    except ImportError:
        return "psutil not installed."
    except Exception as e:
        return f"Failed: {e}"

def get_ram_usage():
    """Get RAM usage"""
    try:
        import psutil
        ram = psutil.virtual_memory()
        used = ram.used // (1024**3)
        total = ram.total // (1024**3)
        percent = ram.percent
        return f"RAM: {used}GB / {total}GB ({percent}%), Sir."
    except ImportError:
        return "psutil not installed."
    except Exception as e:
        return f"Failed: {e}"

def kill_process(name):
    """Kill a process by name"""
    try:
        result = subprocess.run(f'taskkill /f /im {name}', shell=True, 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return f"Killed process {name}, Sir."
        return f"Process {name} not found, Sir."
    except Exception as e:
        return f"Failed: {e}"

def set_wallpaper(path):
    """Set desktop wallpaper"""
    try:
        import ctypes
        if not Path(path).exists():
            return f"Wallpaper file not found: {path}, Sir."
        ctypes.windll.user32.SystemParametersInfoW(20, 0, path, 0)
        return f"Wallpaper set to {path}, Sir."
    except Exception as e:
        return f"Failed to set wallpaper: {e}"

# =========== COMMAND PROCESSING ===========
def process_command(text):
    """Process voice command - SUPER AGENT MODE"""
    if not text:
        return "No input, Sir."
    
    text_lower = text.lower()
    
    # Exit
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return "STOP"
    
    # Help
    if 'help' in text_lower:
        return """JARVIS SUPER AGENT COMMANDS:
        
SYSTEM:
- Lock screen / Sleep / Shutdown / Restart
- Cancel shutdown
- System info / Battery / CPU / RAM
- Minimize all windows
        
APPS & FILES:
- Open [app] / Open folder [path]
- Create file [name] / Create folder [name]
- Delete [file/folder] / List files
- Set wallpaper [path]
        
INTERNET:
- Search for [query]
        
INPUT:
- Type [text] / Press [key]
- Click / Mouse position
- Get clipboard / Copy [text]
        
MEDIA:
- Volume up / down / mute
        
SCREEN:
- Take screenshot
        
PROCESS:
- Kill process [name]
        
TIME:
- What time is it? / What day is it?
        
OTHER:
- History / Help / Run command [cmd]"""
    
    # History
    if 'history' in text_lower:
        if not command_history:
            return "No history yet, Sir."
        lines = [f"{h['timestamp']}: {h['command']} -> {h['response']}" 
                  for h in command_history[-10:]]
        return "Last 10 commands:\n" + "\n".join(lines)
    
    # Time
    if 'time' in text_lower:
        return f"The time is {datetime.now().strftime('%I:%M %p')}, Sir."
    
    # Date
    if 'day' in text_lower or 'date' in text_lower:
        return f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, Sir."
    
    # =========== SYSTEM COMMANDS ===========
    
    # Lock screen
    if any(p in text_lower for p in ['lock screen', 'lock pc', 'lock computer']):
        result = lock_screen()
        save_history(text, result)
        return result
    
    # Sleep
    if any(p in text_lower for p in ['sleep', 'sleep pc', 'sleep computer']):
        result = sleep_pc()
        save_history(text, result)
        return result
    
    # Shutdown
    if 'shutdown' in text_lower:
        if 'cancel' in text_lower:
            result = cancel_shutdown()
        elif 'in ' in text_lower:
            try:
                delay = int([w for w in text.split() if w.isdigit()][0])
                result = shutdown_pc(delay)
            except:
                result = shutdown_pc(60)
        else:
            result = shutdown_pc(10)
        save_history(text, result)
        return result
    
    # Restart
    if 'restart' in text_lower:
        if 'cancel' in text_lower:
            result = cancel_shutdown()
        else:
            result = restart_pc(10)
        save_history(text, result)
        return result
    
    # System info
    if 'system info' in text_lower or 'system information' in text_lower:
        return get_system_info()
    
    # Battery
    if 'battery' in text_lower:
        return get_battery()
    
    # CPU
    if 'cpu' in text_lower and 'usage' in text_lower:
        return get_cpu_usage()
    
    # RAM
    if 'ram' in text_lower or 'memory' in text_lower:
        return get_ram_usage()
    
    # Minimize all
    if any(p in text_lower for p in ['minimize all', 'show desktop', 'desktop']):
        result = minimize_all()
        save_history(text, result)
        return result
    
    # =========== MEDIA COMMANDS ===========
    
    # Volume
    if 'volume up' in text_lower or 'increase volume' in text_lower:
        result = control_volume('up')
        save_history(text, result)
        return result
    
    if 'volume down' in text_lower or 'decrease volume' in text_lower:
        result = control_volume('down')
        save_history(text, result)
        return result
    
    if 'mute' in text_lower or 'volume mute' in text_lower:
        result = control_volume('mute')
        save_history(text, result)
        return result
    
    # =========== SCREEN COMMANDS ===========
    
    # Screenshot
    if 'screenshot' in text_lower or 'take screenshot' in text_lower:
        result = take_screenshot()
        save_history(text, result)
        return result
    
    # =========== INPUT COMMANDS ===========
    
    # Type text
    if text_lower.startswith('type '):
        msg = text.split('type ', 1)[-1].strip()
        result = type_text(msg)
        save_history(text, result)
        return result
    
    # Press key
    if text_lower.startswith('press '):
        key = text.split('press ')[-1].strip()
        result = press_key(key)
        save_history(text, result)
        return result
    
    # Click
    if 'click' in text_lower:
        result = click()
        save_history(text, result)
        return result
    
    # Mouse position
    if 'mouse position' in text_lower or 'where is my mouse' in text_lower:
        return get_mouse_position()
    
    # Clipboard
    if 'clipboard' in text_lower:
        if 'copy' in text_lower or 'set clipboard' in text_lower:
            msg = text.split('copy ')[-1].strip() if 'copy ' in text_lower else text.split('clipboard ')[-1].strip()
            result = set_clipboard(msg)
        else:
            result = get_clipboard()
        save_history(text, result)
        return result
    
    # =========== FILE COMMANDS ===========
    
    # Create file
    if text_lower.startswith('create file '):
        name = text.split('create file ')[-1].strip()
        result = create_file(name)
        save_history(text, result)
        return result
    
    # Create folder
    if text_lower.startswith('create folder ') or text_lower.startswith('make folder '):
        name = text.split('folder ')[-1].strip()
        result = create_folder(name)
        save_history(text, result)
        return result
    
    # Delete
    if text_lower.startswith('delete '):
        name = text.split('delete ')[-1].strip()
        result = delete_file(name)
        save_history(text, result)
        return result
    
    # List files
    if 'list files' in text_lower or 'show files' in text_lower:
        path = "." 
        if 'in ' in text_lower:
            path = text.split('in ')[-1].strip()
        result = list_files(path)
        return result
    
    # Open folder
    if 'open folder' in text_lower:
        path = text.split('open folder ')[-1].strip() if 'open folder ' in text_lower else None
        result = open_folder(path)
        save_history(text, result)
        return result
    
    # Set wallpaper
    if 'wallpaper' in text_lower or 'set wallpaper' in text_lower:
        words = text.split()
        if len(words) > 2:
            path = ' '.join(words[2:]).strip()
            result = set_wallpaper(path)
            save_history(text, result)
            return result
        return "Please specify wallpaper path, Sir."
    
    # =========== PROCESS COMMANDS ===========
    
    # Kill process
    if 'kill process' in text_lower or 'end task' in text_lower:
        name = text.split('process ')[-1].strip() if 'process ' in text_lower else text.split('task ')[-1].strip()
        result = kill_process(name)
        save_history(text, result)
        return result
    
    # =========== APP COMMANDS ===========
    
    # Open apps
    for trigger in ['open ', 'launch ']:
        if trigger in text_lower:
            app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
            if ' and ' in app:
                app = app.split(' and ')[0].strip()
            if app:
                result = open_app(app)
                save_history(text, result)
                return result
    
    # Search
    if 'search for ' in text_lower:
        query = text_lower.split('search for ')[-1].strip()
        if query:
            result = search_web(query)
            save_history(text, result)
            return result
    
    # Run command
    if 'run command' in text_lower or 'execute' in text_lower:
        cmd = text.split('command ')[-1].strip() if 'command ' in text_lower else text.split('execute ')[-1].strip()
        result = run_command(cmd)
        save_history(text, result)
        return result
    
    # =========== COMPOUND COMMANDS ===========
    
    if 'open ' in text_lower and 'search for ' in text_lower:
        parts = text_lower.split(' and ')
        app_part = next((p for p in parts if 'open ' in p), '')
        search_part = next((p for p in parts if 'search for ' in p), '')
        
        if app_part and search_part:
            app = app_part.split('open ')[-1].strip()
            query = search_part.split('search for ')[-1].strip()
            open_result = open_app(app)
            search_result = search_web(query)
            result = f"{open_result} {search_result}"
            save_history(text, result)
            return result
    
    result = "Sorry, I didn't understand, Sir. Say 'Help' for all commands."
    save_history(text, result)
    return result

# =========== MAIN LOOP ===========
def main():
    print("\n" + "="*60)
    print("  SUPER AGENT STATUS")
    print("="*60)
    print(f"  TTS: {'OK - Ready' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK - Ready' if STT_OK else 'Failed'}")
    print(f"  History: {len(command_history)} entries loaded")
    print("="*60)
    print("\n  NEW: Full PC Control - Files, Apps, System, Media")
    print("="*60 + "\n")
    
    speak("JARVIS Super Agent online. I can now control your entire PC, Sir.")
    
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
