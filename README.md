# Marketingkolabs - 24/7 Autonomous Local Voice Agent

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-green.svg)](https://www.python.org)

A **fully autonomous, 24/7 local voice agent** that works for you around the clock. No cloud, no API calls, no dependencies on external services. Your personal AI assistant that runs locally on your machine.

## Key Features

🤖 **24/7 Autonomous Operation** - Works continuously in background, proactive suggestions
🎙️ **Sub-2s Voice Response** - Whisper tiny + Phi-3 Mini for instant responses
🧠 **Persistent Memory** - Remembers conversations, preferences, and patterns across sessions
🔒 **100% Local** - No data leaves your machine, complete privacy
🎨 **Premium UI** - GSAP animations, Framer Motion, glassmorphism design
⌨️ **Customizable Shortcuts** - Every shortcut configurable via settings UI
📋 **Voice-to-Fill** - Say text, auto-fill browser forms and input fields
🌐 **Browser Automation** - Search, compare products, research, extract data
🔧 **Plugin System** - Community-contributed skills, hot-reload support
🖥️ **System Tray** - Runs quietly in background, always available
🚀 **Auto-Start** - Launches on system boot (Windows/Linux/macOS)
🔗 **P2P Sync** - Sync across devices via local network (experimental)

## Architecture

```
┌─────────────────┐
│                  24/7 Autonomous Loop                   │
│  ┌──────────┐    ┌───────────┐    ┌──────────────┐  │
│  │ Monitor  │───▶│ Suggest  │───▶│ Execute     │  │
│  │ System   │    │ Actions  │    │ Proactively │  │
│  └──────────┘    └───────────┘    └──────────────┘  │
└─────────────────┘
         ▲                    │
         │                    ▼
┌─────────────────┐    ┌───────────────┐
│  Voice Input   │    │  Persistent   │
│  (Whisper)    │───▶│  Memory DB   │
└─────────────────┘    └───────────────┘
         │                    ▲
         ▼                    │
┌─────────────────┐          │
│ Intent Parser  │          │
│ (Phi-3 Mini)  │──────────┘
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  Skill Router  │
│  (Plugins)     │
└─────────────────┘
         │
         ▼
┌─────────────────┐
│  TTS Confirm   │
│  (Piper)       │
└─────────────────┘
```

## Quick Start

### 1. Prerequisites

```bash
# Install Ollama for local LLM
curl -fsSL https://ollama.com/install.sh | sh
ollama pull phi3:mini

# Install Piper TTS
# Linux: snap install piper
# Windows: Download from https://github.com/rhasspy/piper
```

### 2. Install Dependencies

```bash
cd marketingkolabs
pip install -r requirements.txt
```

### 3. Run Modes

**Interactive Mode (with Premium UI):**
```bash
python agent.py --mode interactive
# Access UI at http://localhost:3000
```

**Service Mode (24/7 Background):**
```bash
python agent.py --mode service
# Runs in background, accessible via system tray
```

**Enable Auto-Start:**
```bash
python agent.py --enable-autostart
```

## Voice Commands

### Core Capabilities
- **"Search for [product]"** - Web search with auto-opened tabs
- **"Compare [A] and [B]"** - Side-by-side product comparison
- **"Research [product]"** - Reviews, specs, alternatives
- **"Open [app]"** - Launch any application
- **"Cut lines 3-5"** - Text editing by voice
- **"Copy that" / "Paste here"** - Clipboard control
- **"Take a screenshot"** - System automation

### Context-Aware Commands
- "Open notepad" → "Close **that**" (understands references)
- "Search headphones" → "Compare **it** with Sony" (remembers context)
- "Open file.txt" → "Delete **that file**" (tracks last file)

### Custom Macros
Create voice shortcuts that chain multiple actions:
```json
{
  "morning routine": {
    "description": "Start my day",
    "actions": [
      {"skill": "app_control", "action": "open_app", "params": {"app_name": "chrome"}},
      {"skill": "browser", "action": "open_url", "params": {"url": "gmail.com"}}
    ]
  }
}
```
Activate with: **"Run morning routine"**

## Global Shortcuts (Customizable)

| Shortcut | Action |
|----------|--------|
| `Ctrl+Shift+V` | Toggle voice mode |
| `Ctrl+Shift+F` | Voice-to-fill (forms) |
| `Ctrl+Shift+S` | Open settings |
| `Ctrl+Shift+R` | Quick research (selected text) |
| `Ctrl+Shift+C` | Clear clipboard |

*All shortcuts customizable via Settings UI*

## Premium UI Features

- **GSAP + Framer Motion** animations
- **Glassmorphism** design with backdrop blur
- **Gradient text** with Inter + Playfair Display fonts
- **Animated voice orb** with pulsing rings
- **Real-time status** panel
- **Settings tab** with shortcut customization
- **Dark theme** optimized for 24/7 use

## Plugin System

Add custom skills in `/skills/` directory:

```python
from skills import BaseSkill

class Skill(BaseSkill):
    def execute(self, action, params):
        # Your code here
        return {"success": True, "message": "Done"}

    def get_actions(self):
        return ["your_action"]
```

The agent auto-discovers and loads new skills on startup.

## Configuration

Edit `config.yaml` for:
- STT model size (tiny/base/small for speed/accuracy tradeoff)
- LLM model selection (phi3:mini vs mistral:7b)
- TTS voice and speed
- Wake word settings (Porcupine)
- Safety confirmations
- Performance tuning

## 24/7 Autonomous Features

- **Proactive Monitoring** - Checks system health, suggests actions
- **Persistent Memory** - SQLite database stores all interactions
- **Smart Suggestions** - Time-based (morning routine, end-of-day wrap-up)
- **Auto-Organization** - Suggests file cleanup for old Downloads
- **System Tray** - Always accessible, shows status
- **P2P Sync** - Experimental multi-device sync via local network

## Testing

```bash
pip install pytest
pytest tests/ -v
```

## Project Structure

```
marketingkolabs/
├── agent.py              # 24/7 autonomous agent entry point
├── api_server.py        # Flask API + WebSocket server
├── config.yaml          # All settings
├── requirements.txt     # Dependencies
├── agent_memory.db      # Persistent memory (auto-created)
├── settings.json        # User settings (auto-created)
├── core/
│   ├── stt.py          # faster-whisper STT
│   ├── intent_parser.py # Ollama LLM JSON parser
│   ├── tts.py          # Piper TTS
│   ├── skill_router.py # Plugin router
│   ├── context.py      # Session state tracking
│   ├── safety.py       # Action confirmations
│   ├── memory.py       # Persistent SQLite memory
│   ├── proactive.py    # 24/7 autonomous loop
│   ├── p2p_sync.py     # Local network sync
│   ├── tray_app.py     # System tray application
│   └── autostart.py   # Cross-platform auto-start
├── skills/
│   ├── text_editor.py  # Text manipulation
│   ├── file_ops.py     # File operations
│   ├── app_control.py  # App control
│   ├── clipboard.py    # Clipboard tasks
│   ├── browser.py      # Browser automation
│   ├── system.py       # Full system access
│   └── macros.py      # Custom voice shortcuts
├── ui/                 # Premium React UI
│   ├── src/
│   │   ├── App.js      # Main React component
│   │   ├── components/
│   │   │   ├── VoiceOrb.js
│   │   │   ├── CommandBar.js
│   │   │   ├── Settings.js
│   │   │   └── StatusPanel.js
│   │   └── hooks/
│   └── package.json
└── tests/
    ├── test_context.py
    ├── test_skills.py
    └── test_safety.py
```

## License

MIT License - See [LICENSE](LICENSE) file

## Contributing

Community contributions welcome!
- Add new skills via pull requests
- Improve voice recognition accuracy
- Create browser automation scripts
- Optimize for lower latency
- Add multi-language support

## Roadmap

- [ ] Wake word training for custom phrases
- [ ] Semantic search across browser tabs
- [ ] Voice biometrics for user recognition
- [ ] Mobile companion app
- [ ] Docker deployment
- [ ] Plugin marketplace

---

**Built with ❤️ for local-first, privacy-focused AI automation**
