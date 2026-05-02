# Marketingkolabs - 100% FREE Quick Start
## NO Admin Rights? NO Credit Card? NO Problem!

---

## What You Get (100% Free, 100% Local)
✅ **Voice Agent** - Talks, listens, executes tasks  
✅ **24/7 Operation** - Runs continuously in background  
✅ **Ollama LLM** - Local AI brain (no API costs)  
✅ **Memory System** - Remembers conversations  
✅ **Proactive Monitoring** - Suggests actions  
✅ **Premium UI** - Glassmorphism, animations (optional)  

**Total Cost: $0.00 Forever**

---

## Step 1: Get Ollama (The Free AI Brain)
1. Download: https://ollama.com/download (no admin needed - portable version available)
2. Extract to your project folder
3. Open terminal in project folder
4. Run: `ollama pull phi3:mini` (2GB download, one-time)

---

## Step 2: Install Python Packages (No Admin)
```bash
# Use --user flag to install without admin
pip install --user requests pyperclip

# Optional UI packages
pip install --user flask flask-socketio
```

---

## Step 3: Run the Agent
```bash
# Simple terminal mode (recommended for beginners)
python autonomous_agent.py

# Or with premium UI
python api_server.py
# Then open: http://localhost:3000
```

---

## Step 4: Talk to Your Agent!
Type commands like:
- "What time is it?"
- "Open calculator"
- "Search for Python tutorials"
- "Remember that I work in Hyderabad"
- "What did I ask you to remember?"

---

## No-Admin Full Portable Setup
If you **can't install anything**, do this:

1. Download **portable Python** (zip version)
2. Download **Ollama** (portable .exe)
3. Extract both to project folder
4. Run this batch file:

```batch
@echo off
set PATH=%~dp0python;%~dp0ollama;%PATH%
start ollama serve
timeout /t 5
ollama run phi3:mini
python autonomous_agent.py
```

---

## File Structure (Simplified)
```
marketingkolabs/
├── autonomous_agent.py      ← START HERE (main agent)
├── requirements_free.txt     ← Free dependencies
├── agent_memory.db          ← Created automatically
├── core/                   ← Advanced features (optional)
└── ui/                     ← Premium UI (optional)
```

---

## Troubleshooting (Free Version)

### "Ollama not found"
→ Download from ollama.com, extract to project folder

### "pip install fails - no permission"
→ Use: `pip install --user <package>`

### "phi3:mini not found"
→ Run: `ollama pull phi3:mini` (needs internet once)

### "pyperclip not working"
→ Normal on some systems, agent still works without it

---

## What Can It Do?

### Voice Commands (with microphone)
- "Search for latest AI news"
- "Open my Documents folder"
- "What's the weather?" (via browser)
- "Remember: I like dark mode"

### Text Commands (type in terminal)
- "Build me a landing page for a restaurant"
- "Compare iPhone vs Samsung"
- "Open Notepad and type 'Hello World'"

### Proactive Features
- Greets you in the morning
- Suggests day-wrap-up at 5 PM
- Remembers your preferences

---

## Upgrade Later (Still Free!)
- Add premium UI: `cd ui && npm install && npm start`
- Add voice input: install `sounddevice` and `faster-whisper`
- Add system tray: install `pystray`

---

**START NOW:**
```bash
python autonomous_agent.py
```

**No signups. No credit cards. No admin password. 100% yours.**
