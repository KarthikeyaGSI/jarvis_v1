# JARVIS SUPER-PREMIUM v2.0 - COMPLETE SYSTEM

## 🚀 Quick Start

### Option 1: Double-Click Launchers (Easiest)
- **RUN_SUPER_PREMIUM.bat** - Full AI-powered Super-Premium Agent with UI
- **RUN_SUPER_AGENT.bat** - CLI Super Agent (no browser needed)
- **RUN_PREMIUM.bat** - Original Premium UI

### Option 2: Command Line
```bash
cd "C:\Users\Student\Downloads\open source voice agent\marketingkolabs"

# Super-Premium with AI brain
python super_premium.py

# Or with web UI
python jarvis_server.py
# Then open: http://localhost:5000
```

## ⚡ What's New in v2.0

### 🤖 AI Brain (Ollama)
- Uses **phi3:mini** or **gemma4:26b** for intelligent responses
- Understands natural language: "Hey JARVIS, tell me a joke"
- Auto-activates when command not recognized
- 100% local, no cloud needed

### 🔧 Self-Healing System
- Auto-installs missing packages (psutil, pyautogui, etc.)
- No manual pip install needed
- Bulletproof error handling

### ✨ Particle Effects UI
- Animated particle network background
- Glowing neon effects on all elements
- Smooth animations and transitions
- Premium dark theme with shimmer effects

### 💻 Full PC Control
- **System**: Lock, Sleep, Shutdown, Restart, Battery, CPU, RAM
- **Apps**: Open any app, search web
- **Files**: Create/open/delete files & folders
- **Media**: Volume up/down/mute
- **Screen**: Screenshot, mouse click, type text
- **AI**: Natural language queries via Ollama

## 📋 Command Examples

### System Control
```
Lock screen
Sleep PC
Shutdown (in 60 seconds)
Cancel shutdown
System info
Battery status
CPU usage
RAM usage
Minimize all windows
```

### App & File Control
```
Open Chrome
Open Notepad
Search for Python tutorials
Create file myfile.txt
Create folder MyProjects
Delete oldfile.txt
Open folder C:\Users\Student\Documents
```

### Media & Input
```
Volume up
Volume down
Mute
Take screenshot
Type Hello World (types at cursor)
Click (clicks mouse)
Clipboard (reads clipboard)
```

### AI Queries (Natural Language)
```
Hey JARVIS, what is quantum computing?
Tell me a joke
Explain how AI works
What's the weather like? (searches web)
```

### Modes
```
voice - Switch to voice mode
text - Switch to text mode
Ctrl+Shift+Space - Quick voice toggle
Help - Show all commands
History - Show last 10 commands
Stop - Exit JARVIS
```

## 📊 Features Checklist

✅ **AI Brain** - Ollama (phi3:mini/gemma4:26b)
✅ **Self-Healing** - Auto-installs missing packages
✅ **Particle UI** - Stunning animated background
✅ **Voice Recognition** - Web Speech API + Whisper STT
✅ **Text-to-Speech** - JARVIS voice (pyttsx3)
✅ **System Control** - Lock, sleep, shutdown, restart
✅ **App Control** - Open any application
✅ **File Operations** - Create, delete, list files/folders
✅ **Media Control** - Volume up/down/mute
✅ **Screen Capture** - Screenshots
✅ **Input Simulation** - Type text, click mouse
✅ **Clipboard** - Read/set clipboard
✅ **Web Search** - Google search integration
✅ **History** - Saves last 200 commands to JSON
✅ **Premium UI** - Neon glow effects, animations
✅ **No Admin Required** - Works on restricted PCs
✅ **100% Local** - No cloud dependencies (except web search)

## 🗂️ File Structure

```
marketingkolabs/
├── super_premium.py          # Main AI-powered agent (CLI)
├── jarvis_server.py           # Flask server for web UI
├── jarvis.py                 # Original JARVIS (basic)
├── static/
│   ├── jarvis_premium.html  # Super-Premium UI with particles
│   └── jarvis.html          # Original Premium UI
├── jarvis_history.json       # Command history (auto-created)
├── RUN_SUPER_PREMIUM.bat    # Launcher for Super-Premium
├── RUN_SUPER_AGENT.bat      # Launcher for CLI agent
└── RUN_PREMIUM.bat          # Launcher for original Premium UI
```

## 🔧 Troubleshooting

### AI Brain Not Working?
```bash
# Check Ollama
ollama list

# Install a model (if needed)
ollama pull phi3:mini
ollama serve
```

### pyautogui Errors?
- Screenshot, type, and click need pyautogui
- Super-Premium auto-installs it, or run:
```bash
pip install pyautogui
```

### Microphone Not Working?
- Check Windows Sound Settings
- Ensure mic is set as default input device
- JARVIS auto-detects Bluetooth/headset mics

### Port 5000 Already in Use?
```bash
# Change port in jarvis_server.py (line ~400)
# Or kill existing process:
netstat -ano | findstr :5000
taskkill /PID <pid> /F
```

## 🎉 You're Ready!

1. Double-click **RUN_SUPER_PREMIUM.bat**
2. Browser opens to JARVIS Premium UI
3. Click microphone or press **Ctrl+Shift+Space** for voice
4. Type commands or speak naturally
5. JARVIS handles the rest with AI intelligence!

**Marketingkolabs - 100% Local AI Agent**
Powered by Python, Ollama, Flask, and pure awesomeness ✨
