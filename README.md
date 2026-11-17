# MarketingKo Labs: Jarvis v1

**Fully autonomous, 24/7 local voice agent and desktop automation system.**

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python)](https://www.python.org/)
[![Faster-Whisper](https://img.shields.io/badge/Speech_to_Text-Faster--Whisper-orange?style=flat-square)](https://github.com/SYSTRAN/faster-whisper)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](#)

---

## Overview

### The Problem It Solves
Modern cloud-based AI assistants introduce noticeable network latency, recurring API costs, privacy concerns, and lack deep system-level integration. Users needing fast voice dictation, continuous background assistance, and desktop workflow automation are often forced to choose between sluggish cloud round-trips and stripped-down local tools.

### Why It Was Built
Developed at MarketingKo Labs, **Jarvis v1** was engineered as the open-source foundational research prototype behind **[SancharyaAI](https://sancharya.marketingko.in/)**. It operates 100% on-device with zero cloud reliance, delivering sub-2-second speech-to-text response times, persistent episodic memory, voice-to-clipboard insertion, and autonomous desktop task orchestration.

---

## Key Features

- **Sub-2-Second Voice Response:** High-throughput local transcription powered by `faster-whisper` (Whisper Tiny / Base with INT8 quantization).
- **24/7 Autonomous Background Operation:** Runs non-intrusively in the system tray, monitoring system state and proactive task triggers.
- **Persistent Local Memory:** SQLite memory engine (`agent_memory.db`) and structured history logs (`jarvis_history.json`) that retain user preferences and context across restarts.
- **Voice-to-Fill & Dictation:** Instant speech-to-clipboard and automated form/input field typing via `pyperclip` and keyboard hooks.
- **Desktop & Web Research Automation:** Built-in research workflows capable of querying browsers, parsing web data, and extracting structured insights.
- **Modular Plugin & Skill System:** Hot-reloadable skill architecture for extending system actions, shortcuts, and custom triggers.
- **OS Autostart Daemons:** Production auto-launch scripts (`autostart.py`, `GO.bat`, `GO_FINAL.ps1`) for uninterrupted background persistence.

---

## Architecture Overview

```
                      ┌──────────────────────────────┐
                      │    Microphone Audio Stream   │
                      └──────────────┬───────────────┘
                                     │ (sounddevice)
                      ┌──────────────▼───────────────┐
                      │     faster-whisper Engine    │
                      │   (Local INT8 Quantization)  │
                      └──────────────┬───────────────┘
                                     │ Transcribed Text
                      ┌──────────────▼───────────────┐
                      │    Autonomous Agent Loop     │
                      │  (Intent Classifier & Router)│
                      └───┬──────────────────────┬───┘
                          │                      │
            ┌─────────────▼──────┐        ┌──────▼─────────────┐
            │ Persistent Memory  │        │   Desktop Action   │
            │  SQLite + History  │        │    Executor        │
            └────────────────────┘        └──────┬─────────────┘
                                                 │
                               ┌─────────────────┼─────────────────┐
                               │                 │                 │
                        ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────┐
                        │Voice-to-Fill│   │ Web Search  │   │   System    │
                        │ (Clipboard) │   │ Automation  │   │  Shortcuts  │
                        └─────────────┘   └─────────────┘   └─────────────┘
```

---

## Tech Stack

- **Core Runtime:** Python 3.9+
- **Speech-to-Text (STT):** `faster-whisper` (CTranslate2 implementation of Whisper)
- **Audio Capture & DSP:** `sounddevice`, `numpy`
- **Memory & Storage:** SQLite (`agent_memory.db`), JSON data stores
- **System Automation:** `pyperclip`, `pyautogui`, platform API bindings
- **Configuration:** YAML (`config.yaml`), customizable hotkey dictionaries

---

## Repository Structure

```
├── agent.py                 # Core agent lifecycle and main event loop
├── autonomous_agent.py      # Background autonomous scheduler and monitor
├── api_server.py            # Local REST bridge for programmatic trigger ingestion
├── autostart.py             # System boot configuration utility
├── config.yaml              # Core audio thresholds, model sizes, and shortcuts
├── jarvis.py                # Primary CLI and desktop entry point
├── jarvis_flow.py           # Multi-step task execution workflow builder
├── jarvis_shortcuts.py      # Hotkey capture and routing handlers
├── agent_memory.db          # Persistent SQLite state database
├── requirements.txt         # Complete dependency manifest
└── GO.bat / GO_FINAL.ps1    # One-click Windows deployment scripts
```

---

## Getting Started

### Prerequisites
- Python 3.9 or higher
- Microphone input device
- Virtual environment tool (`venv` or `uv`)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/KarthikeyaGSI/jarvis_v1.git
cd jarvis_v1
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Verify your microphone device:
```bash
python TEST_NOW.py
```

5. Launch the voice agent:
```bash
python jarvis.py
```

Or on Windows, launch directly using the runner script:
```powershell
.\GO_FINAL.ps1
```

---

## Configuration (`config.yaml`)

```yaml
audio:
  model_size: "tiny"       # options: tiny, base, small
  sample_rate: 16000
  silence_threshold: 0.015
  silence_duration: 1.2    # seconds of silence before processing

agent:
  auto_copy: true          # automatically copy dictation to clipboard
  autonomous_mode: true    # enable background task execution
  log_level: "INFO"
```

---

## Evolution to SancharyaAI

Jarvis v1 represents the initial local desktop agent experiment created at MarketingKo Labs. The lessons learned in audio turn-taking, acoustic chunking, and intent classification laid the architectural groundwork for **[SancharyaAI](https://sancharya.marketingko.in/)**, an enterprise-grade cloud AI voice platform for telephony and outbound automation.

---

## License

This project is open-source under the [MIT License](LICENSE).

---

## Author

**Karthikeya Thallapally**  
Founder, [MarketingKo](https://marketingko.in/) & [SancharyaAI](https://sancharya.marketingko.in/)  
Twitter / X: [@thekarthgsi](https://twitter.com/thekarthgsi) · GitHub: [@KarthikeyaGSI](https://github.com/KarthikeyaGSI)
