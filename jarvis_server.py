"""
JARVIS API Server - Premium UI Backend
Serves the stunning JARVIS interface and handles voice commands
"""
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO, emit
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
app.config['SECRET_KEY'] = 'jarvis-premium'
socketio = SocketIO(app, cors_allowed_origins="*")

# ============ State ============
command_count = 0
xp = 0
level = 1
voice_mode = "Ready"

# History storage
command_history = []
MAX_HISTORY = 50
HISTORY_FILE = Path(__file__).parent / 'jarvis_history.json'

# Load history
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
    """Save to history"""
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

# Try to import TTS
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

# Try to import STT
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
        'voice_mode': voice_mode,
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
    """Process text command and return response"""
    text_lower = text.lower()
    
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return {'message': 'Goodbye, Sir. JARVIS deactivating.'}
    
    if 'help' in text_lower:
        return {'message': '''Available commands, Sir:
- Open Chrome / Notepad / Calculator
- Search for [query]
- What time is it?
- History
- Stop / Goodbye'''}
    
    if 'history' in text_lower:
        if not command_history:
            return {'message': 'No history yet, Sir.'}
        lines = [f"{h['timestamp']}: {h['command']} -> {h['response']}" 
                  for h in command_history[-10:]]
        return {'message': 'Last 10 commands:\n' + '\n'.join(lines)}
    
    if 'time' in text_lower:
        now = datetime.now().strftime("%I:%M %p")
        return {'message': f'The time is {now}, Sir.'}
    
    if 'day' in text_lower or 'date' in text_lower:
        now = datetime.now().strftime("%A, %B %d, %Y")
        return {'message': f'Today is {now}, Sir.'}
    
    for trigger in ['open ', 'launch ']:
        if trigger in text_lower:
            app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
            if ' and ' in app:
                app = app.split(' and ')[0].strip()
            if app:
                return open_application(app)
    
    if 'search for ' in text_lower:
        query = text_lower.split('search for ')[-1].strip()
        if query:
            return search_web(query)
    
    return {'message': "I didn't understand that, Sir. Say 'Help' for commands."}


def open_application(name):
    """Open application"""
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
    }
    exe = app_map.get(name, name)
    
    try:
        subprocess.Popen(f'start "" "{exe}"', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return {'message': f'Opening {name}, Sir.'}
    except:
        try:
            subprocess.Popen(f'start "" "{exe}.exe"', shell=True)
            return {'message': f'Opening {name}, Sir.'}
        except Exception as e:
            return {'message': f'Failed to open {name}: {str(e)}'}


def search_web(query):
    """Search web"""
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return {'message': f'Searching for {query}, Sir.'}
    except Exception as e:
        return {'message': f'Search failed: {str(e)}'}


# ============ TTS ============
def speak_jarvis(text):
    """Speak with JARVIS personality"""
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


# ============ WebSocket ============
@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')
    emit('status', {'status': 'connected'})

@socketio.on('voice_command')
def handle_voice_command(data):
    text = data.get('text', '')
    if text:
        result = process_text_command(text)
        emit('response', result)


# ============ Main ============
def start_server():
    """Start the JARVIS server"""
    logger.info("=" * 60)
    logger.info("  JARVIS - Just A Rather Very Intelligent System")
    logger.info("=" * 60)
    logger.info(f"  TTS: {'OK' if TTS_OK else 'Failed'}")
    logger.info(f"  STT: {'OK' if STT_OK else 'Failed'}")
    logger.info(f"  History: {len(command_history)} entries")
    logger.info("=" * 60)
    logger.info("  JARVIS UI: http://localhost:5000")
    logger.info("=" * 60)
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    start_server()
