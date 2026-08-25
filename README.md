<div align="center">

# ⚡ ORION — AI Voice PC Assistant
### **Operational Responsive Intelligent Orchestration Network**

*A local, privacy-first, voice-controlled Windows desktop assistant powered by offline machine learning, local Whisper speech recognition, gated automation, and a modern GUI dashboard.*

<br/>

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?style=for-the-badge&logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Tests](https://img.shields.io/badge/Tests-110%20Passed-2EA44F?style=for-the-badge&logo=pytest&logoColor=white)](https://docs.pytest.org/)
[![Privacy](https://img.shields.io/badge/Privacy-100%25%20Local%20%26%20Offline-7057ff?style=for-the-badge)](https://github.com/omorfarukullas/ORION)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Project Roadmap & Status](#-project-roadmap--status)
- [Supported Commands & Utterances](#-supported-commands--utterances)
- [Safety & Trust Framework](#-safety--trust-framework)
- [Quick Start Guide](#-quick-start-guide)
- [Configuration Reference](#-configuration-reference)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Known Limitations & Future Roadmap](#-known-limitations--future-roadmap)
- [Author & License](#-author--license)

---

## 🌟 Overview

**ORION** (*Operational Responsive Intelligent Orchestration Network*) is a modular, offline-first personal voice assistant designed specifically for PC automation. Unlike cloud-tethered voice assistants, ORION processes everything **locally on your machine** — ensuring maximum privacy, zero data telemetry, and predictable execution.

ORION continuously listens in a lightweight standby mode, detects the wake word (**`"ORION"`**), captures command speech using energy-based Voice Activity Detection (VAD), transcribes audio with local OpenAI Whisper, parses intents and entities through a trained scikit-learn NLP model, checks destructive actions against a security gate with spoken confirmation, executes system-level PC automations, and speaks the results using synthesized offline speech while displaying live telemetry on a desktop dashboard.

---

## ✨ Key Features

- **🎙️ Zero-Cloud Voice Pipeline**:
  - **Wake Word Detection**: Ultra-low-latency local standby listening for keyword **`"ORION"`** (or *"Hey ORION"*).
  - **Speech-to-Text**: Fast offline transcription via OpenAI Whisper (`base` model, ~140MB local weights).
  - **Text-to-Speech**: Instant, clear speech responses powered by `pyttsx3` with adjustable rate and volume.
  - **Smart VAD**: Dynamic RMS Voice Activity Detection that automatically trims leading/trailing silence.

- **🧠 Machine Learning NLP Pipeline**:
  - **Intent Classifier**: TF-IDF n-gram vectorizer + Logistic Regression classifier trained across 34 intents with **99.50% accuracy**.
  - **Entity Extractor**: Robust regex and slot-filling extractor for apps, URLs, file paths, math expressions, and geolocations.
  - **Rule-Based Engine**: Sub-millisecond keyword fallback engine for guaranteed execution of core commands.
  - **Confidence Gating**: 3-tier execution protocol (`>70%` execute, `45–70%` confirm, `<45%` clarify).

- **🛡️ 3-Tier Security & Safety Gating**:
  - **Safe Commands**: Immediate execution for non-destructive actions (media, web searches, apps, diagnostics).
  - **Destructive Commands**: Mandatory spoken Yes/No verification loop before executing destructive tasks (`DELETE_FILE`, `SHUTDOWN`, `RESTART`).
  - **Forbidden Policies**: Hard rejection of arbitrary shell injections or unauthorized directory modifications.
  - **Audit Logging**: Structured JSON-Lines audit trail (`logs/audit.jsonl`) recording every action and timestamp.

- **⚡ Multi-Step Task Planner**:
  - Decomposes composite utterances connected by conjunctions (*"and"*, *"then"*, *"after that"*) into ordered single-intent tasks.
  - Linear sequential execution with aggregated spoken response feedback.

- **🤖 Local LLM Integration**:
  - Offline local question answering via **Ollama** API (`llama3.2`, `mistral`, etc.) for creative queries, fallback definitions, or code snippets, respecting 100% user privacy.

- **💾 Short-Term Context & Persistent Memory**:
  - **Conversational Context**: Resolves follow-up pronouns and references (e.g., *"open Chrome"* ➔ *"close it"*, *"search YouTube for it"*).
  - **SQLite Memory Store**: Remembers user-defined facts (e.g., *"remember that my project folder is on Desktop"*) with exact and fuzzy recall.

- **🎨 Modern CustomTkinter Dashboard & Settings Panel**:
  - Live state monitor (`IDLE`, `LISTENING`, `PROCESSING`, `SPEAKING`, `ERROR`).
  - Real-time hardware telemetry bar (CPU %, RAM used/total GB, Battery %).
  - Real-time Last Command card displaying speech transcript, intent, confidence, and extracted entities.
  - Scrollable, color-coded execution history with instant Clear functionality.
  - Live **Settings tab** to adjust confidence thresholds, toggle Ollama LLM, configure TTS rate, switch GUI theme, and save settings to a persistent `config/user_settings.json` file.

---

## 🏗️ System Architecture

### Processing Pipeline

```
[ Microphone Input ]
         │
         ▼
[ Wake Word Detector ]  ──(Standby: openWakeWord)
         │  (Triggered!)
         ▼
[ VAD & Audio Listener ] ──(Dynamic RMS silence cutoff)
         │
         ▼
[ Whisper STT Engine ]  ──(Local transcription)
         │
         ▼
[ Task Planner / Splitter ] ──(Conjunction parsing: "and", "then")
         │
         ▼
[ NLP Command Parser ]  ──(Preprocessing ➔ TF-IDF Classifier ➔ Entity Extractor)
         │
         ▼
[ Context Resolver ]    ──(Resolves pronouns: "it", "that", "the file")
         │
         ▼
[ Security Gating ]     ──(SAFE ➔ Execute | DESTRUCTIVE ➔ Spoken Yes/No | FORBIDDEN ➔ Refuse)
         │
         ▼
[ Action Dispatcher ]   ──(Apps, Files, Browser, System, Media, Screenshots, Weather, Calculator, Clipboard, Ollama LLM, Database)
         │
         ├──────────────────────────┐
         ▼                          ▼
[ pyttsx3 TTS ]            [ CustomTkinter Dashboard & SQLite ]
(Spoken feedback)          (Live metrics, settings, history & persistent memory)
```

### Directory Structure

```
ORION/
├── app.py                      # System entrypoint and main orchestration engine
├── config/
│   ├── settings.py             # Global settings singleton (parameters & thresholds)
│   ├── applications.json       # App alias mapping to Windows paths
│   ├── commands.json           # Keyword pattern rules for fallback engine
│   └── user_settings.json      # Persistent user settings overrides
├── data/
│   ├── intents.csv             # Classifier training corpus (34 intents, 200+ samples)
│   └── training_data.json      # Entity extraction slot schemas
├── models/                     # Serialized machine learning models (.pkl)
│   ├── tfidf_vectorizer.pkl
│   └── intent_classifier.pkl
├── speech/
│   ├── wake_word.py            # Local wake word detector (openWakeWord)
│   ├── listener.py             # Microphone buffer listener with RMS VAD
│   ├── speech_to_text.py       # Local OpenAI Whisper transcription pipeline
│   └── text_to_speech.py       # pyttsx3 offline text-to-speech engine
├── nlp/
│   ├── preprocessing.py        # Tokenizer, stop-word filter, and word stemmer
│   ├── intent_classifier.py    # TF-IDF + Logistic Regression classifier
│   ├── entity_extractor.py     # Regex/keyword slot-filling extractor
│   ├── rule_engine.py          # Fast keyword rule matching engine
│   ├── command_parser.py       # Unified NLP parsing orchestrator
│   └── command_dispatcher.py   # Safety-gated and memory-backed command router
├── planner/
│   ├── task_planner.py         # Multi-step conjunction task planner
│   └── context.py              # Short-term conversational context tracker
├── actions/
│   ├── applications.py         # App launcher (Registry/PATH) & process terminator
│   ├── browser.py              # Web searches, YouTube lookups, and navigation
│   ├── files.py                # Scoped file system operations (CRUD)
│   ├── system.py               # Hardware diagnostics, shutdown & restart
│   ├── media.py                # Virtual multimedia keyboard controls
│   ├── screenshots.py          # Screenshot capture with clipboard path copying
│   ├── weather.py              # Weather forecast utilizing free Open-Meteo API
│   ├── calculator.py           # Safe AST mathematical expression evaluator
│   ├── clipboard.py            # Clipboard read/copy/clear manager
│   └── llm.py                  # Local LLM generator wrapper for Ollama REST API
├── security/
│   ├── command_validator.py    # Risk assessment (SAFE, DESTRUCTIVE, FORBIDDEN)
│   ├── confirmation.py         # Dynamic spoken Yes/No verification loop
│   └── permissions.py          # Allowed write paths validation & audit logging
├── database/
│   └── database.py             # SQLite persistence engine for memory and history
├── gui/
│   ├── dashboard.py            # CustomTkinter root window and event dispatcher
│   ├── status.py               # State indicator widget with color-coded dot
│   ├── metrics.py              # Live CPU/RAM/Battery auto-refreshing bar
│   ├── history.py              # Scrollable command execution history panel
│   └── settings_panel.py       # GUI Settings tab widget for live calibration
├── utils/
│   ├── logger.py               # Dual-sink rotating file & terminal logger
│   └── helpers.py              # Text normalizer, time formatters, byte units
└── tests/
    ├── test_actions.py         # PC Automation unit tests
    ├── test_context.py         # Context pronoun resolution unit tests
    ├── test_database.py        # SQLite persistence and memory recall tests
    ├── test_entities.py        # Slot extractor unit tests
    ├── test_gui.py             # GUI widget and dashboard unit tests
    ├── test_integration.py     # End-to-end integration and roundtrip tests
    ├── test_intent.py          # NLP Intent classifier unit tests
    ├── test_planner.py         # TaskPlanner multi-step parsing tests
    ├── test_rule_engine.py     # Rule engine fallback tests
    ├── test_security.py        # Safety gating, permissions & audit tests
    ├── test_speech_input.py    # Wake word, listener, and VAD tests
    └── test_new_features.py    # Weather, calculator, clipboard, Ollama and settings tests
```

---

## 📌 Project Roadmap & Status

| Phase | Module | Scope | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | **Scaffold & Setup** | Directory structure, settings singleton, logging, and base stubs | **✅ Complete** |
| **Phase 2** | **Speech Output** | Local Text-to-Speech voice engine (`pyttsx3`) | **✅ Complete** |
| **Phase 3** | **Speech Input** | Microphone listener, RMS VAD, and local Whisper transcription | **✅ Complete** |
| **Phase 4** | **Wake Word** | Standby wake word loop using `openWakeWord` (`"hey_jarvis"`) | **✅ Complete** |
| **Phase 5** | **Rule-Based Engine** | Keyword pattern matching and immediate fallback execution | **✅ Complete** |
| **Phase 6** | **NLP Classifier** | TF-IDF & Logistic Regression intent classifier (99.5% accuracy) | **✅ Complete** |
| **Phase 7** | **Entity Extractor** | Slot-filling entity extractor and unified `CommandParser` | **✅ Complete** |
| **Phase 8** | **PC Automation** | Execution adapters (Apps, Files, Browser, System, Media, Screen) | **✅ Complete** |
| **Phase 9** | **Safety Gating** | 3-tier risk validator, spoken confirmation gate, and audit logging | **✅ Complete** |
| **Phase 10** | **User Interface** | Modern `CustomTkinter` GUI dashboard, status monitor, and metrics | **✅ Complete** |
| **Phase 11** | **Memory System** | Conversational context tracking and persistent SQLite memory | **✅ Complete** |
| **Phase 12** | **Polish & Demo** | Multi-step task planner, complete documentation, 92 passed unit tests | **✅ Complete** |
| **Phase 13** | **Feature Expansion**| Weather lookup, calculator, clipboard manager, local Ollama integration, GUI Settings panel with persistence, and 18 additional unit tests | **✅ Complete** |

---

## 🗣️ Supported Commands & Utterances

ORION recognizes a rich set of distinct intents across several functional categories:

| Category | Example Spoken Utterance | Assistant Action & Behavior |
|:---|:---|:---|
| **App Management** | `"ORION, open Chrome"` | Launches Google Chrome via Registry or PATH |
| | `"ORION, close Chrome"` | Terminates running Chrome processes via `psutil` |
| | `"ORION, close it"` | Resolves pronoun from context and closes active app |
| **Web & Browsing** | `"ORION, search Google for Python tutorials"` | Opens default browser with Google query |
| | `"ORION, search YouTube for lofi music"` | Opens YouTube search results |
| | `"ORION, open github.com"` | Navigates directly to target URL |
| **File Management** | `"ORION, create a folder called AI_Projects"` | Creates folder on Desktop / workspace |
| | `"ORION, create a file called notes.txt"` | Creates empty file in workspace |
| | `"ORION, find file notes.txt"` | Fast scoped search across Desktop/Documents/Downloads |
| | `"ORION, rename notes.txt to final.txt"` | Renames target file |
| | `"ORION, delete file temp.txt"` | **Prompts for spoken confirmation** before deleting |
| **System Diagnostics** | `"ORION, what is my CPU usage?"` | Reports current CPU utilization percentage |
| | `"ORION, how much RAM am I using?"` | Reports used and total RAM in GB |
| | `"ORION, check battery level"` | Reports battery percentage and charging state |
| | `"ORION, system summary"` | Speaks complete CPU, RAM, and Battery overview |
| **Media Controls** | `"ORION, play music"` / `"ORION, pause"` | Sends virtual media play/pause keypress |
| | `"ORION, next track"` / `"previous track"` | Skips to next or previous media track |
| | `"ORION, volume up"` / `"volume down"` / `"mute"` | Adjusts or toggles system master volume |
| **Time & Utility** | `"ORION, what time is it?"` | Speaks current local time |
| | `"ORION, what is today's date?"` | Speaks current day and date |
| | `"ORION, take a screenshot"` | Captures screen to `screenshots/` and copies path to clipboard |
| **Weather Forecast** | `"ORION, what is the weather in London?"` | Geocodes and fetches real-time temperature & conditions |
| **Calculator** | `"ORION, what is 25 times 4?"` / `"calculate 15 percent of 800"` | Safely parses and evaluates mathematical expressions |
| **Clipboard** | `"ORION, copy Hello World to clipboard"` / `"what is in my clipboard?"` | Performs clipboard read/copy/clear |
| **Ollama Local AI** | `"ORION, explain quantum computing"` | Routes complex creative queries to local LLM |
| **Memory & Facts** | `"ORION, remember that my project is on Desktop"` | Persists key-value fact into SQLite database |
| | `"ORION, what is my project?"` | Recalls memory via exact or fuzzy key matching |
| **Multi-Step Tasks** | `"ORION, open Chrome and search YouTube for AI"` | Splits on conjunction and executes sequentially |
| **System Power** | `"ORION, shut down the computer"` | **Prompts for spoken confirmation** before shutdown |
| | `"ORION, restart the computer"` | **Prompts for spoken confirmation** before restart |

---

## 🔒 Safety & Trust Framework

ORION is designed around defensive automation principles:

```
                      [ Classified Intent ]
                                │
               ┌────────────────┼────────────────┐
               ▼                ▼                ▼
          [ SAFE ]       [ DESTRUCTIVE ]   [ FORBIDDEN ]
               │                │                │
               │         (Spoken Prompt)         │
               │    "Should I continue? (Yes/No)"│
               │                │                │
               │        Confirmed? (Whisper)     │
               │        ├── Yes ──► Execute      │
               │        └── No  ──► Cancel       │
               │                                 │
               ▼                                 ▼
      [ Execute Action ]                 [ Block & Refuse ]
               │                                 │
               └────────────────┬────────────────┘
                                ▼
                       [ Audit Logging ]
                      (logs/audit.jsonl)
```

1. **SAFE (Immediate Execution)**: All non-destructive read operations, searches, media keys, and safe creations.
2. **DESTRUCTIVE (Confirmation Required)**: File deletion and system power commands (`SHUTDOWN`, `RESTART`, `DELETE_FILE`). ORION asks: *"You asked me to [action]. Should I continue?"* and waits for an explicit *"yes"* before proceeding.
3. **FORBIDDEN (Hard Rejection)**: Arbitrary shell execution or modification of system files outside allowed roots.
4. **Filesystem Boundary**: File creation and modification are restricted to `ALLOWED_WRITE_ROOTS` (`Desktop`, `Documents`, `Downloads`).

---

## 🚀 Quick Start Guide

### 📋 Prerequisites
- **Windows 10 / 11 (64-bit)**
- **Python 3.11+**
- **Microsoft Visual C++ 14.0+ Redistributable** (required for `sounddevice` and `openWakeWord`)
- Working microphone and audio output device

### ⚙️ Installation

1. **Clone the repository**:
   ```powershell
   git clone https://github.com/omorfarukullas/ORION.git
   cd ORION
   ```

2. **Create and activate a Python virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install all required dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify model files**:
   *(Pre-trained models are created automatically, but you can retrain at any time)*:
   ```powershell
   python nlp/intent_classifier.py
   ```

### 🏃 Running ORION

Launch the full application:
```powershell
python app.py
```

- The modern **CustomTkinter Dashboard** will appear.
- Say the wake word: **`"Hey Jarvis"`** *(or the configured wake phrase)*.
- ORION will chime: *"Yes?"*.
- Speak your command (e.g. *"Open Chrome and search YouTube for Python tutorials"*).

---

## ⚙️ Configuration Reference

All settings can be customized in the GUI Settings panel or directly in `config/settings.py`:

| Parameter | Default Value | Description |
|:---|:---:|:---|
| `WAKE_WORD` | `"hey_jarvis"` | Model name for openWakeWord detection |
| `WAKE_WORD_THRESHOLD` | `0.50` | Activation threshold for wake word detector (0.0–1.0) |
| `WHISPER_MODEL` | `"base"` | Whisper model size (`tiny`, `base`, `small`, `medium`) |
| `WHISPER_DEVICE` | `"cpu"` | Inference hardware (`cpu` or `cuda`) |
| `CONFIDENCE_EXECUTE` | `0.70` | Minimum confidence score to execute command immediately |
| `CONFIDENCE_CONFIRM` | `0.45` | Threshold below which ORION confirms intent interpretation |
| `VAD_SILENCE_THRESHOLD` | `0.01` | RMS amplitude cutoff for voice activity detection |
| `VAD_SILENCE_DURATION` | `1.5` | Seconds of silence before stopping recording |
| `TTS_RATE` | `180` | Speech rate in words per minute |
| `TTS_VOLUME` | `0.9` | Speech synthesizer volume (0.0–1.0) |
| `GUI_THEME` | `"dark"` | Dashboard theme (`dark`, `light`, `system`) |
| `GUI_COLOR_THEME` | `"blue"` | CustomTkinter accent color |
| `OLLAMA_ENABLED` | `True` | Whether local Ollama LLM integration is active |
| `OLLAMA_URL` | `"http://localhost:11434"` | Address of the local Ollama service |
| `OLLAMA_MODEL` | `"llama3.2"` | Default LLM model name |

---

## 🧪 Testing & Quality Assurance

ORION includes a comprehensive unit and integration test suite covering all modules:

```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

### Test Suite Coverage (110 Tests)

| Test Module | Tests | Focus Area | Status |
|:---|:---:|:---|:---:|
| `test_actions.py` | 19 | App process spawning, browser, system stats, files, media | ✅ Passed |
| `test_entities.py` | 15 | Regex slot extraction, URL/file matching, memory slots | ✅ Passed |
| `test_security.py` | 11 | Risk classification, allowlist checks, confirmation loop | ✅ Passed |
| `test_intent.py` | 13 | Classifier training, TF-IDF vectorization, confidence gating | ✅ Passed |
| `test_speech_input.py` | 11 | Sound buffer listener, VAD silence cutoff, Whisper STT | ✅ Passed |
| `test_rule_engine.py` | 7 | Pattern matching rules and keyword extraction fallback | ✅ Passed |
| `test_planner.py` | 5 | Multi-step conjunction splitting and sequential execution | ✅ Passed |
| `test_database.py` | 4 | SQLite command logging, key-value memory CRUD, fuzzy recall | ✅ Passed |
| `test_gui.py` | 4 | StatusPanel, HistoryPanel, MetricsBar, Dashboard window | ✅ Passed |
| `test_integration.py` | 4 | End-to-end roundtrip tests (memory, safety, multi-step) | ✅ Passed |
| `test_context.py` | 3 | Short-term context tracking and pronoun resolution | ✅ Passed |
| `test_new_features.py` | 12 | Weather, calculator, clipboard, Ollama and settings tests | ✅ Passed |
| `test_vector_classifier.py`| 2 | Vector classifier intent validation and fallback | ✅ Passed |
| **Total** | **110** | **100% Passing Test Suite** | **✅ Passed** |

---

## ⚠️ Known Limitations & Future Roadmap

- **Windows Optimized**: Process management and App Paths lookups utilize Windows APIs (`winreg`, `psutil`). Multi-platform support (Linux/macOS) is planned for V2.
- **Single-User Scope**: SQLite database is currently scoped for a single local profile.
- **Language Support**: Default acoustic and intent models are calibrated for English (`en`).
- **Upcoming V2 Capabilities**:
  - `send2trash` integration for reversible file deletion.
  - Global system hotkey toggle (`Win + Space`).

---

## 👨‍💻 Author & License

Developed with ❤️ by **Omor Faruck Ullas**  
- **Email**: [omor.farukh16@gmail.com](mailto:omor.farukh16@gmail.com)  
- **Repository**: [github.com/omorfarukullas/ORION](https://github.com/omorfarukullas/ORION)

This project is licensed under the **MIT License** — see the `LICENSE` file for details.