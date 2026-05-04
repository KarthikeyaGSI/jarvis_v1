"""
JARVIS SUPER AGENT - Premium UI Backend
Full PC Control via Beautiful Web Interface
"""
from flask import Flask, send_from_directory, jsonify, request
from pathlib import Path
import sys
import logging
import subprocess
import threading
import time
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'jarvis-super-agent'
socketio = SocketIO(app, cors_allowed_origins="*")

# ============ State ============
command_count = 0
xp = 0
level = 1

# History
command_history = []
MAX_HISTORY = 100
HISTORY_FILE = Path(__file__).parent / 'jarvis_history.json'

try:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line.strip())
                command_history.append(entry)
        command_history[:] = command_history[-MAX_HISTORY:]
        logger.info(f"[HISTORY] Loaded {len(command_history)} entries")
except:
    pass

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

# ============ TTS ============
try:
    import pyttsx3
    tts = pyttsx3.init()
    tts.setProperty('rate', 130)
    voices = tts.getProperty('voices')
    if voices:
        for v in voices:
            if 'en' in v.id.lower() and 'female' not in v.id.lower():
                tts.setProperty('voice', v.id)
                break
    TTS_OK = True
except:
    TTS_OK = False
    tts = None

# ============ STT ============
try:
    from faster_whisper import WhisperModel
    stt_model = WhisperModel('tiny', device='cpu', compute_type='int8')
    STT_OK = True
except:
    STT_OK = False
    stt_model = None

# ============ Routes ============
@app.route('/')
def index():
    return send_from_directory('static', 'jarvis.html')

@app.route('/api/status')
def get_status():
    return jsonify({
        'status': 'ONLINE',
        'commands': command_count,
        'xp': xp,
        'level': level,
        'tts_ok': TTS_OK,
        'stt_ok': STT_OK,
        'history_count': len(command_history)
    })

@app.route('/api/command', methods=['POST'])
def process_command():
    global command_count, xp, level
    
    data = request.json
    text = data.get('command', '').strip()
    
    if not text:
        return jsonify({'error': 'No command provided'}), 400
    
    logger.info(f"[COMMAND] Processing: '{text}'")
    command_count += 1
    xp += 5
    level = (xp // 100) + 1
    
    result = process_text_command(text)
    
    if result.get('message'):
        save_history(text, result['message'])
        if TTS_OK:
            speak_jarvis(result['message'])
    
    return jsonify(result)

@app.route('/api/history')
def get_history():
    return jsonify({'history': command_history[-10:]})

@app.route('/api/speak', methods=['POST'])
def speak_text():
    if not TTS_OK:
        return jsonify({'error': 'TTS not available'}), 400
    
    data = request.json
    text = data.get('text', '')
    if text:
        speak_jarvis(text)
        return jsonify({'success': True})
    return jsonify({'error': 'No text'}), 400

# ============ Command Processing ============
def process_text_command(text):
    """Process command - SUPER AGENT MODE"""
    if not text:
        return {'message': 'No input, Sir.'}
    
    text_lower = text.lower()
    
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return {'message': 'Goodbye, Sir. JARVIS deactivating.'}
    
    if 'help' in text_lower:
        return {'message': '''JARVIS SUPER AGENT COMMANDS:
        
SYSTEM: Lock screen, Sleep, Shutdown, Restart, System info, Battery, CPU, RAM
APPS: Open [app], Search for [query]
FILES: Create file/folder, Delete, List files, Open folder
MEDIA: Volume up/down/mute
SCREEN: Take screenshot
INPUT: Type [text], Press [key], Click, Mouse position
UTILS: History, Help, Minimize all, Clipboard'''
        }
    
    if 'history' in text_lower:
        if not command_history:
            return {'message': 'No history yet, Sir.'}
        lines = [f"{h['timestamp']}: {h['command']} -> {h['response']}" 
                  for h in command_history[-10:]]
        return {'message': 'Last 10 commands:\n' + '\n'.join(lines)}
    
    if 'time' in text_lower:
        return {'message': f"The time is {datetime.now().strftime('%I:%M %p')}, Sir."}
    
    if 'day' in text_lower or 'date' in text_lower:
        return {'message': f"Today is {datetime.now().strftime('%A, %B %d, %Y')}, Sir."}
    
    # System commands
    if any(p in text_lower for p in ['lock screen', 'lock pc']):
        return {'message': lock_screen()}
    
    if 'shutdown' in text_lower:
        if 'cancel' in text_lower:
            return {'message': cancel_shutdown()}
        return {'message': shutdown_pc(10)}
    
    if 'restart' in text_lower:
        return {'message': restart_pc(10)}
    
    if 'sleep' in text_lower:
        return {'message': sleep_pc()}
    
    if 'system info' in text_lower:
        return {'message': get_system_info()}
    
    if 'battery' in text_lower:
        return {'message': get_battery()}
    
    if 'cpu' in text_lower and 'usage' in text_lower:
        return {'message': get_cpu_usage()}
    
    if 'ram' in text_lower or 'memory' in text_lower:
        return {'message': get_ram_usage()}
    
    if 'minimize all' in text_lower or 'desktop' in text_lower:
        return {'message': minimize_all()}
    
    # Media
    if 'volume up' in text_lower:
        return {'message': control_volume('up')}
    if 'volume down' in text_lower:
        return {'message': control_volume('down')}
    if 'mute' in text_lower:
        return {'message': control_volume('mute')}
    
    # Screen
    if 'screenshot' in text_lower:
        return {'message': take_screenshot()}
    
    # Input
    if text_lower.startswith('type '):
        msg = text.split('type ', 1)[-1].strip()
        return {'message': type_text(msg)}
    
    if 'click' in text_lower:
        return {'message': click()}
    
    if 'clipboard' in text_lower:
        return {'message': get_clipboard()}
    
    # Files
    if text_lower.startswith('create file '):
        name = text.split('create file ')[-1].strip()
        return {'message': create_file(name)}
    
    if 'create folder' in text_lower:
        name = text.split('create folder ')[-1].strip()
        return {'message': create_folder(name)}
    
    if text_lower.startswith('delete '):
        name = text.split('delete ')[-1].strip()
        return {'message': delete_file(name)}
    
    if 'open folder' in text_lower:
        path = text.split('open folder ')[-1].strip() if 'open folder ' in text_lower else None
        return {'message': open_folder(path)}
    
    # Apps
    for trigger in ['open ', 'launch ']:
        if trigger in text_lower:
            app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
            if app:
                return {'message': open_app(app)}
    
    if 'search for ' in text_lower:
        query = text_lower.split('search for ')[-1].strip()
        if query:
            return {'message': search_web(query)}
    
    return {'message': "I didn't understand. Say 'Help' for all commands, Sir."}

# ============ PC Control Functions ============
def open_app(name):
    app_map = {
        'chrome': 'chrome', 'notepad': 'notepad', 'calculator': 'calc',
        'explorer': 'explorer', 'word': 'winword', 'spotify': 'spotify',
    }
    exe = app_map.get(name.lower(), name.lower())
    try:
        subprocess.Popen(f'start "" "{exe}"', shell=True, stdout=subprocess.PIPE)
        return f"Opening {name}, Sir."
    except:
        return f"Failed to open {name}."

def search_web(query):
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching for {query}, Sir."
    except Exception as e:
        return f"Search failed: {e}"

def take_screenshot():
    try:
        import pyautogui
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        pyautogui.screenshot(filename)
        return f"Screenshot saved as {filename}, Sir."
    except ImportError:
        return "pyautogui not installed. Run: pip install pyautogui"
    except Exception as e:
        return f"Screenshot failed: {e}"

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
        return f"Volume control failed: {e}"

def lock_screen():
    try:
        os.system('rundll32.exe user32.dll,LockWorkStation')
        return "Locking screen, Sir."
    except Exception as e:
        return f"Failed: {e}"

def sleep_pc():
    try:
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
        return "Putting PC to sleep, Sir."
    except Exception as e:
        return f"Failed: {e}"

def shutdown_pc(delay=0):
    try:
        subprocess.Popen(f'shutdown /s /t {delay}', shell=True)
        return f"Shutting down in {delay} seconds, Sir."
    except Exception as e:
        return f"Failed: {e}"

def restart_pc(delay=0):
    try:
        subprocess.Popen(f'shutdown /r /t {delay}', shell=True)
        return f"Restarting in {delay} seconds, Sir."
    except Exception as e:
        return f"Failed: {e}"

def cancel_shutdown():
    try:
        subprocess.Popen('shutdown /a', shell=True)
        return "Shutdown cancelled, Sir."
    except Exception as e:
        return f"Failed: {e}"

def get_system_info():
    try:
        import platform
        info = f"OS: {platform.system()} {platform.release()}\n"
        info += f"Version: {platform.version()}\n"
        info += f"Machine: {platform.machine()}\n"
        info += f"Python: {platform.python_version()}, Sir."
        return info
    except Exception as e:
        return f"Failed: {e}"

def get_battery():
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            return f"Battery: {battery.percent}% ({'plugged in' if battery.power_plugged else 'on battery'}), Sir."
        return "No battery detected, Sir."
    except ImportError:
        return "psutil not installed. Run: pip install psutil"
    except Exception as e:
        return f"Failed: {e}"

def get_cpu_usage():
    try:
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        return f"CPU usage: {cpu}%, Sir."
    except ImportError:
        return "psutil not installed."
    except Exception as e:
        return f"Failed: {e}"

def get_ram_usage():
    try:
        import psutil
        ram = psutil.virtual_memory()
        used = ram.used // (1024**3)
        total = ram.total // (1024**3)
        return f"RAM: {used}GB / {total}GB ({ram.percent}%), Sir."
    except ImportError:
        return "psutil not installed."
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
        import shutil
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

def open_folder(path=None):
    try:
        if path is None:
            path = os.getcwd()
        subprocess.Popen(f'explorer "{path}"')
        return f"Opened {path}, Sir."
    except Exception as e:
        return f"Failed: {e}"

def type_text(text):
    try:
        import pyautogui
        time.sleep(2)
        pyautogui.write(text)
        return f"Typed: {text}, Sir."
    except ImportError:
        return "pyautogui not installed."
    except Exception as e:
        return f"Failed: {e}"

def click(x=None, y=None):
    try:
        import pyautogui
        if x and y:
            pyautogui.click(x, y)
        else:
            pyautogui.click()
        return "Clicked, Sir."
    except ImportError:
        return "pyautogui not installed."
    except Exception as e:
        return f"Failed: {e}"

def get_clipboard():
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        return f"Clipboard: {content[:100]}..., Sir." if content else "Clipboard empty, Sir."
    except Exception as e:
        return f"Failed: {e}"

def minimize_all():
    try:
        os.system('powershell -Command (New-Object -ComObject WScript.Shell).SendKeys("^d")')
        return "Minimized all windows, Sir."
    except Exception as e:
        return f"Failed: {e}"

# ============ TTS ============
def speak_jarvis(text):
    if not tts:
        return
    styled = f"Sir, {text}" if not text.startswith('Sir') else text
    def _speak():
        try:
            tts.say(styled)
            tts.runAndWait()
        except:
            pass
    threading.Thread(target=_speak, daemon=True).start()

# ============ Main ============
def start_server():
    logger.info("="*60)
    logger.info("  JARVIS SUPER AGENT - Full PC Control")
    logger.info("="*60)
    logger.info(f"  TTS: {'OK' if TTS_OK else 'Failed'}")
    logger.info(f"  STT: {'OK' if STT_OK else 'Failed'}")
    logger.info(f"  History: {len(command_history)} entries")
    logger.info("="*60)
    logger.info("  JARVIS UI: http://localhost:5000")
    logger.info("="*60)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    start_server()
