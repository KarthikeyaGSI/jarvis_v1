"""
JARVIS - 100% WORKING VERSION
- History stored in JSON file (survives restarts)
- Text + Voice modes
- NO admin required
"""
import os
import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Get script directory
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

print("\n" + "="*60)
print("  JARVIS - Just A Rather Very Intelligent System")
print("="*60)
print(f"\n[INIT] Working from: {SCRIPT_DIR}")
print("[INIT] Starting JARVIS...\n")

# =========== History Storage ===========
command_history = []
MAX_HISTORY = 50
HISTORY_FILE = SCRIPT_DIR / 'jarvis_history.json'

def save_history(command, response):
    """Save command + response to history (in-memory + JSON file)"""
    entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'response': response
    }
    command_history.append(entry)
    if len(command_history) > MAX_HISTORY:
        command_history.pop(0)
    
    # Append to JSON file (survives restart)
    try:
        with open(HISTORY_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    except Exception as e:
        print(f"[HISTORY ERROR] {e}")

# Load existing history from file
try:
    if HISTORY_FILE.exists():
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                entry = json.loads(line.strip())
                command_history.append(entry)
        # Keep only last MAX_HISTORY
        command_history[:] = command_history[-MAX_HISTORY:]
        print(f"[HISTORY] Loaded {len(command_history)} entries")
except Exception as e:
    print(f"[HISTORY] Load error: {e}")

# =========== TTS ===========
print("[TTS] Initializing...")
tts_engine = None
TTS_OK = False

try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 130)  # JARVIS speed
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
    """Speak with JARVIS style"""
    if not tts_engine or not text:
        return
    try:
        styled = f"Sir, {text}" if not text.startswith('Sir') else text
        tts_engine.say(styled)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"[TTS ERROR] {e}")

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
    
    # Find Bluetooth mic
    import sounddevice as sd
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev['max_input_channels'] > 0:
            name = dev['name'].lower()
            if 'bluetooth' in name or 'headset' in name or 'airbass' in name:
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
    """Listen and transcribe"""
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

# =========== PC Control ===========
def open_app(name):
    """Open application"""
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
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

# =========== Command Processing ===========
def process_command(text):
    """Process voice command"""
    if not text:
        return "No input, Sir."
    
    text_lower = text.lower()
    
    # Exit
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return "STOP"
    
    # Help
    if 'help' in text_lower:
        return """Available commands, Sir:
- Open Chrome / Notepad / Calculator
- Search for [query]
- What time is it?
- History
- Stop / Goodbye"""
    
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
    
    # Compound commands: "open X and search for Y"
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
    
    result = "Sorry, I didn't understand, Sir. Say 'Help' for commands."
    save_history(text, result)
    return result

# =========== Main Loop ===========
def main():
    print("\n" + "="*60)
    print("  SYSTEM STATUS")
    print("="*60)
    print(f"  TTS: {'OK - Ready' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK - Ready' if STT_OK else 'Failed'}")
    print(f"  History: {len(command_history)} entries loaded")
    print("="*60 + "\n")
    
    speak("JARVIS online. Type commands or say 'voice' for voice mode.")
    
    mode = 'text'  # text or voice
    
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
                    
                    # Check for mode switch
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
