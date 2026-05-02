"""
MARKETINGKOLABS - SIMPLE WORKING VERSION
Guaranteed to speak and show feedback!
"""
import os
import sys
import time
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*60)
print("  MARKETINGKOLABS - SIMPLE VOICE AGENT")
print("="*60)
print("\n[INIT] Starting...\n")

# =========== TTS (Simplest working version) ===========
print("[TTS] Initializing...")
try:
    import pyttsx3
    tts_engine = pyttsx3.init()
    tts_engine.setProperty('rate', 150)
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
    TTS_OK = False
    tts_engine = None

def speak(text):
    """Speak - simple blocking version"""
    if not tts_engine or not text:
        return
    try:
        print(f"\n[AGENT SPEAKS]: {text}")
        tts_engine.say(text)
        tts_engine.runAndWait()
    except Exception as e:
        print(f"[TTS ERROR]: {e}")

# =========== STT (Whisper) ===========
print("\n[STT] Initializing...")
try:
    from faster_whisper import WhisperModel
    stt_model = WhisperModel('tiny', device='cpu', compute_type='int8')
    STT_OK = True
    print("[STT] OK - Ready")
except Exception as e:
    print(f"[STT] Failed: {e}")
    STT_OK = False
    stt_model = None

def listen(timeout=5):
    """Listen and transcribe"""
    if not stt_model:
        print("[STT] Not ready")
        return ""
    
    try:
        import sounddevice as sd
        import numpy as np
        
        print("\n[LISTENING... Speak now!]")
        
        # Find Bluetooth mic
        mic_id = None
        try:
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
        except:
            pass
        
        # Record
        recording = sd.rec(
            int(16000 * timeout),
            samplerate=16000,
            channels=1,
            dtype='float32',
            device=mic_id
        )
        sd.wait()
        
        # Transcribe
        segments, _ = stt_model.transcribe(recording.flatten(), language='en', vad_filter=False)
        text = " ".join(s.text for s in segments).strip()
        
        if text:
            print(f"[HEARD]: '{text}'")
        else:
            print("[NO SPEECH DETECTED]")
        
        return text
        
    except Exception as e:
        print(f"[STT ERROR]: {e}")
        return ""

# =========== PC Control ===========
def open_app(name):
    """Open application"""
    app_map = {
        'chrome': 'chrome', 'browser': 'chrome', 'google chrome': 'chrome',
        'notepad': 'notepad', 'calculator': 'calc', 'cmd': 'cmd',
        'explorer': 'explorer', 'firefox': 'firefox',
    }
    exe = app_map.get(name.lower(), name.lower())
    
    try:
        subprocess.Popen(f'start "" "{exe}"', shell=True)
        return f"Opened {name}"
    except:
        try:
            subprocess.Popen(f'start "" "{exe}.exe"', shell=True)
            return f"Opened {name}"
        except Exception as e:
            return f"Failed: {e}"

def search_web(query):
    """Search web"""
    try:
        import webbrowser
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return f"Searching: {query}"
    except Exception as e:
        return f"Search failed: {e}"

# =========== Command Processing ===========
def process_command(text):
    """Process voice command"""
    if not text:
        return "No input"
    
    text_lower = text.lower()
    
    # Exit
    if any(w in text_lower for w in ['exit', 'quit', 'stop', 'goodbye']):
        return "STOP"
    
    # Help
    if 'help' in text_lower:
        return """Commands:
- Open Chrome / Notepad / Calculator
- Search for [query]
- What time is it?
- Stop / Goodbye"""
    
    # Time
    if 'time' in text_lower:
        from datetime import datetime
        return f"The time is {datetime.now().strftime('%I:%M %p')}"
    
    # Open apps
    for trigger in ['open ', 'launch ']:
        if trigger in text_lower:
            app = text_lower.split(trigger)[-1].strip().strip(' .,!?')
            if app:
                return open_app(app)
    
    # Search
    if 'search for ' in text_lower:
        query = text_lower.split('search for ')[-1].strip()
        if query:
            return search_web(query)
    
    return "Sorry, didn't understand. Say 'Help' for commands."

# =========== Main Loop ===========
def main():
    print("\n" + "="*60)
    print("  SYSTEM STATUS")
    print("="*60)
    print(f"  TTS: {'OK - Ready' if TTS_OK else 'Failed'}")
    print(f"  STT: {'OK - Ready' if STT_OK else 'Failed'}")
    print("="*60 + "\n")
    
    speak("System ready! Type commands or say voice for voice mode.")
    
    mode = 'text'  # text or voice
    
    while True:
        try:
            if mode == 'text':
                try:
                    user_input = input("\n[YOU] ")
                except EOFError:
                    break
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'voice':
                    mode = 'voice'
                    print("\n[SWITCHED TO VOICE MODE]")
                    speak("Voice mode activated. Speak commands.")
                    continue
                
                if user_input.lower() == 'text':
                    mode = 'text'
                    print("\n[SWITCHED TO TEXT MODE]")
                    continue
                
                print(f"\n[PROCESSING...]")
                result = process_command(user_input)
                
                if result == "STOP":
                    print("\n[STOPPING...]")
                    speak("Goodbye!")
                    break
                
                print(f"[AGENT] {result}\n")
                speak(result)
            
            else:  # voice mode
                text = listen()
                if text:
                    print(f"\n[PROCESSING...]")
                    result = process_command(text)
                    
                    if result == "STOP":
                        print("\n[STOPPING...]")
                        speak("Goodbye!")
                        break
                    
                    print(f"[AGENT] {result}\n")
                    speak(result)
                    
                    # Check for mode switch
                    if 'text' in text.lower():
                        mode = 'text'
                        print("\n[SWITCHED TO TEXT MODE]")
                        continue
        
        except KeyboardInterrupt:
            print("\n\n[STOPPED]")
            speak("Goodbye!")
            break
        except Exception as e:
            print(f"\n[ERROR]: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
