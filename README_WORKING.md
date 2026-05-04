# JARVIS SUPER AGENT - WORKING VERSION

## Quick Start
**Double-click** `RUN_JARVIS_WORKING.bat`

Or from command line:
```bash
cd "C:\Users\Student\Downloads\open source voice agent\marketingkolabs"
python jarvis_working.py
```

## What Works

### AI Brain (Ollama)
- Uses **phi3:mini** locally (no cloud needed)
- Understands natural language: "Hey JARVIS, tell me a joke"
- Auto-activates for unrecognized commands

### Scheduled Tasks (NEW!)
```
Remind me in 5 minutes to check email
Remind me at 14:30 to join meeting
Run "Take screenshot" every 10 minutes
Repeat "Battery" every 30 minutes
List scheduled tasks
Remove task 0
```

### System Control
```
Lock screen        |  Sleep PC
Shutdown (in 60s)  |  Cancel shutdown
Restart PC          |  System info
Battery status      |  CPU usage
RAM usage          |  Minimize all windows
```

### Apps & Files
```
Open Chrome        |  Search for Python
Create file test.txt |  Create folder Projects
Delete old.txt     |  Open folder C:\Users
Take screenshot    |  Type Hello World
Click              |  Clipboard
```

### Media & Input
```
Volume up/down/mute |  Type [text]
Click mouse         |  Mouse position
Get clipboard     |  Set clipboard [text]
```

### Utilities
```
History            |  Help
What time is it?  |  What day is it?
Stop               |  voice (switch mode)
text (switch)      |  Ctrl+Shift+Space (voice)
```

## Files
```
jarvis_working.py      - Main working agent (CLI)
jarvis_server.py        - Flask server for web UI
static/jarvis.html    - Premium UI
RUN_JARVIS_WORKING.bat - Launcher (double-click)
jarvis_history.json    - Command history
jarvis_schedule.json   - Scheduled tasks
```

## Troubleshooting

**AI not working?**
```bash
ollama list              # Check models
ollama pull phi3:mini  # Install model
ollama serve           # Start service
```

**Scheduler not working?**
- Check `jarvis_schedule.json` is created
- Tasks auto-save after each change
- Use "List scheduled tasks" to see active tasks

**Unicode errors?**
- This version has NO emojis/unicode that break Windows console
- All output is pure ASCII-safe

## You're Ready!

1. Double-click `RUN_JARVIS_WORKING.bat`
2. Type commands or say 'voice' for voice mode
3. Try: "Remind me in 5 minutes to check email"
4. JARVIS handles everything with AI intelligence!

**Built by Marketingkolabs**
**Powered by Python, Ollama, Flask & Pure Awesomeness**
