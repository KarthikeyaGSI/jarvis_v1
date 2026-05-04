# JARVIS SUPER-PREMIUM v2.0 - QUICK REFERENCE

## 🚀 Quick Start
**Double-click** `RUN_SUPER_PREMIUM.bat` → Opens browser → Start commanding!

## ⏰ Scheduled Tasks (NEW!)

### One-Time Reminders
```
Remind me in 5 minutes to check email
Remind me in 2 hours to take break
Remind me at 14:30 to join meeting
Set reminder in 30 seconds to test
```

### Recurring Tasks
```
Run "Take screenshot" every 10 minutes
Repeat "Open Chrome" every hour
Run "Check battery" every 30 minutes
```

### Manage Tasks
```
List scheduled tasks
Show scheduled tasks
Remove task 0
Delete task 1
```

## 🤖 AI Brain (Ollama)
```
Hey JARVIS, tell me a joke
Explain quantum computing
What's the weather like? (searches web)
```

## 💻 System Control
```
Lock screen              |  Sleep PC
Shutdown (in 60s)      |  Cancel shutdown
Restart PC              |  System info
Battery status          |  CPU usage
RAM usage              |  Minimize all windows
```

## 📱 Apps & Files
```
Open Chrome             |  Search for Python
Create file test.txt   |  Create folder Projects
Delete old.txt          |  Open folder C:\Users
Take screenshot        |  Type Hello World
Click                   |  Clipboard
```

## 🎵 Media & Input
```
Volume up/down/mute    |  Type [text]
Click mouse            |  Mouse position
Get clipboard          |  Set clipboard [text]
```

## 🔧 Utilities
```
History                 |  Help
What time is it?       |  What day is it?
Stop                    |  voice (switch mode)
text (switch to text)  |  Ctrl+Shift+Space (voice)
```

## 📋 Real Examples

### Schedule a meeting reminder
```
You: Remind me at 15:00 to join team meeting
JARVIS: Task scheduled for 03:00 PM, Sir.
```

### Auto-screenshot every hour
```
You: Run "Take screenshot" every 1 hour
JARVIS: Task will repeat every 3600 seconds, Sir.
```

### Recurring battery check
```
You: Repeat "Battery" every 30 minutes
JARVIS: Task will repeat every 1800 seconds, Sir.
```

### Check scheduled tasks
```
You: List scheduled tasks
JARVIS: 
  [0] test reminder - repeats every 5s (executed 3 times)
  [1] 10 second reminder - scheduled for 09:46 AM
```

## 🎉 Features Checklist

✅ **AI Brain** - Ollama phi3:mini (local, no cloud)
✅ **Scheduled Tasks** - Reminders, recurring tasks, timed commands
✅ **Self-Healing** - Auto-installs missing packages
✅ **Particle UI** - Stunning animated background
✅ **Voice + Text** - Dual input modes
✅ **Full PC Control** - System, apps, files, media
✅ **History** - Last 200 commands saved to JSON
✅ **No Admin** - Works on restricted PCs
✅ **100% Local** - Your data stays with you

## 🛠️ Troubleshooting

**AI not working?**
```bash
ollama list              # Check models
ollama pull phi3:mini  # Install model
ollama serve           # Start Ollama service
```

**Scheduler not working?**
- Check `jarvis_schedule.json` is created
- Tasks auto-save after each change
- Use "List scheduled tasks" to see active tasks

**Voice not working?**
- Ensure mic is default input device
- Check Windows Sound Settings
- JARVIS auto-detects Bluetooth headsets

## 📁 Files
```
super_premium.py          - Main AI agent with scheduling
jarvis_server.py           - Flask web server
static/jarvis_premium.html - Particle-effect UI
jarvis_history.json        - Command history
jarvis_schedule.json      - Scheduled tasks
RUN_SUPER_PREMIUM.bat    - Double-click launcher
```

## 🎊 You're All Set!

1. **Double-click** `RUN_SUPER_PREMIUM.bat`
2. **Browser opens** to JARVIS Premium UI
3. **Click mic** 🎤 or press `Ctrl+Shift+Space`
4. **Speak naturally** - "Hey JARVIS, remind me in 10 minutes..."
5. **JARVIS handles everything** with AI intelligence!

**Built with ❤️ by Marketingkolabs**
**Powered by Python, Ollama, Flask & Pure Awesomeness ✨**
