# ORION — AI Voice PC Assistant

> **Operational Responsive Intelligent Orchestration Network**
>
> A local, privacy-centric, voice-controlled PC assistant. ORION operates offline, runs local wake-word detection, transcribes spoken commands with local Whisper, processes NLP intent/entities using a machine learning pipeline, executes gated automation actions, and replies using synthesized speech.

---

## 📌 Project Status

| Phase | Module | Scope | Status |
| :--- | :--- | :--- | :---: |
| **Phase 1** | **Scaffold & Setup** | Directory structure, dependencies, configurations, logging, and stubs | **✅ Complete** |
| **Phase 2** | **Speech Output** | Offline Text-to-Speech (`pyttsx3`) | **✅ Complete** |
| **Phase 3** | **Speech Input** | Mic listening with Voice Activity Detection (VAD) & local Whisper transcription | **✅ Complete** |
| **Phase 4** | **Wake Word** | Idle/standby wake word loop (`openWakeWord`) | **✅ Complete** |
| **Phase 5** | **Rule-Based Engine** | Hard-coded command execution | **✅ Complete** |
| **Phase 6** | **NLP Classifier** | TF-IDF & Logistic Regression intent classifier | **✅ Complete** |
| **Phase 7** | **Entity Extractor** | Named-entity matching & command parser | **✅ Complete** |
| **Phase 8** | **PC Automation** | Execution adapters (Browser, Apps, Media, Screenshots, Files, System) | **✅ Complete** |
| **Phase 9** | **Safety Gating** | Permissions validation, destructiveness warnings, confirmation handlers | **✅ Complete** |
| **Phase 10** | **User Interface** | GUI dashboard (`CustomTkinter`), history, and status monitor | 🔲 Pending |
| **Phase 11** | **Memory System** | Conversational context and persistent database (`SQLite`) | 🔲 Pending |
| **Phase 12** | **Polish & Demo** | Comprehensive test passes, multi-step actions validation | 🔲 Pending |

---

## 🛠️ Architecture Map

The project is structured modularly from day one to keep modules isolated, testable, and maintainable.

```
ORION/
├── app.py                      # System bootstrapper and orchestration engine
├── config/
│   ├── settings.py             # Config singleton (parameters, thresholds, models)
│   ├── applications.json       # App alias mapping to local Windows absolute paths
│   └── commands.json           # Regex/keyword patterns for Phase 5 parser
├── data/
│   ├── intents.csv             # Structured classifier training dataset
│   └── training_data.json      # Entity extraction slot-filling schemas
├── models/                     # Git-ignored serialized machine learning models (.pkl)
├── speech/
│   ├── wake_word.py            # Local wake word detector (openWakeWord)
│   ├── listener.py             # Sound device microphone buffer listener
│   ├── speech_to_text.py       # Local Whisper transcription pipeline
│   └── text_to_speech.py       # Offline pyttsx3 voice engine
├── nlp/
│   ├── preprocessing.py        # Tokenizer, stop-word filter, and stemmer
│   ├── intent_classifier.py    # Intent classifier (TF-IDF + Logistic Regression)
│   ├── entity_extractor.py     # Regex/keyword entity extractor
│   └── command_parser.py       # Pipeline connecting Preprocessing -> Intent -> Entities
├── planner/
│   ├── task_planner.py         # Multi-step task parsing and linear workflow planning
│   └── context.py              # Short-term dynamic conversation state tracking
├── actions/
│   ├── applications.py         # App process manager (spawn and kill processes)
│   ├── browser.py              # Browser execution (searches, direct navigation)
│   ├── files.py                # File system manager (directories, file templates)
│   ├── system.py               # Hardware system diagnostics and state
│   ├── media.py                # Media key simulation (PyAutoGUI virtual keys)
│   └── screenshots.py          # Pillow-based screenshot capturing utility
├── security/
│   ├── command_validator.py    # Risk assessment and policy rules check
│   ├── confirmation.py         # Dynamic audio/text prompt verification handler
│   └── permissions.py          # Write-allowlist verification & audit logs
├── database/
│   └── database.py             # SQLite persistence engine for memory and history
├── gui/
│   ├── dashboard.py            # CustomTkinter base window frame
│   ├── status.py               # Component for assistant status (idle/listening/working)
│   └── history.py              # Component displaying command execution logs
├── utils/
│   ├── logger.py               # Double-sink file & terminal logger
│   └── helpers.py              # Text normalizer, time helpers, byte formatter
└── tests/
    ├── test_intent.py          # Classifier training verification tests
    ├── test_entities.py        # Entity slot parser verification tests
    ├── test_actions.py         # OS-level execution driver unit tests
    └── test_security.py        # Security validator policy tests
```

---

## 🚀 Setup & Execution

### 📋 Prerequisites
- **Python 3.11+**
- **Windows OS** (Primary platform target)
- **Microsoft Visual C++ Redistributable** (Required for wake-word dependencies)

### ⚙️ Quick Installation

1. Navigate to the project root directory:
   ```powershell
   cd c:\Users\omorf\Desktop\ORION
   ```

2. Create a clean virtual environment:
   ```powershell
   python -m venv venv
   ```

3. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

### 🏃 Running ORION

Start the assistant backend:
```powershell
python app.py
```

### 🧪 Test Execution

Ensure the scaffolding integrity and security risk configurations by running the test suite:
```powershell
.\venv\Scripts\python.exe -m pytest tests/ -v
```

---

## 🔒 Safety and Trust System

ORION enforces a strict security protocol mapped to three security categories:

### Risk Classifications

1. **Safe (Immediate Execution)**
   - System Info queries (`SYSTEM_CPU`, `SYSTEM_RAM`, `SYSTEM_BATTERY`).
   - Web browser actions (`WEB_SEARCH`, `YOUTUBE_SEARCH`, `OPEN_WEBSITE`).
   - App controls (`OPEN_APP`, `CLOSE_APP`).
   - Multimedia controls (`PLAY_MEDIA`, `VOLUME_UP`, etc.).

2. **Destructive (Explicit confirmation gate required)**
   - File deletion (`DELETE_FILE`).
   - Operating system command (`SHUTDOWN`, `RESTART`).

3. **Forbidden (Security risk - rejected)**
   - Arbitrary shell executions.
   - Registry configuration alterations.

---

## ⚙️ Core Configuration

Configurations can be edited inside `config/settings.py`. Key thresholds are listed below:

| Property | Default Value | Purpose |
| :--- | :--- | :--- |
| `CONFIDENCE_EXECUTE` | `0.80` | High confidence: execute command immediately |
| `CONFIDENCE_CONFIRM` | `0.50` | Medium confidence: prompt user for voice/text validation |
| `< CONFIDENCE_CONFIRM` | — | Low confidence: ask user for command clarification |
| `WAKE_WORD` | `"hey_jarvis"` | Target phrase model for local listening wake-up |
| `WHISPER_MODEL` | `"base"` | Model size used for transcription (~140MB local download) |