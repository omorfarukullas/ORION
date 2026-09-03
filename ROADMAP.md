# 🗺️ ORION Future Roadmap (v2.0 — v5.0)

This roadmap outlines the long-term evolutionary path for **ORION (Operational Responsive Intelligent Orchestration Network)** as an open-source, daily-driver desktop AI operating layer.

---

## 📅 Roadmap Overview

```
v1.0 (Core Engine)        ──► v2.0 (Open-Source Daily Driver)  ──► v3.0 (Ecosystem & Multi-Platform)
- Whisper STT / VAD            - Windows Inno Setup .exe             - Linux & macOS Native Ports
- openWakeWord Standby         - FastAPI + WebSocket Web UI          - Coqui / Piper Neural TTS
- 99.5% TF-IDF Intent          - Selectable Voice Personas           - Community Plugin Hub
- Safety Gating                - Cloud Plugin Registry (GitHub)      - Multi-turn Dialogue Manager
- SQLite Memory                - CustomTkinter V2 Dashboard          - Home Assistant & IoT

v4.0 (Autonomous Agent)   ──► v5.0 (Ubiquitous Ambient Intelligence)
- Dynamic Computer Use         - Air-gapped Enterprise RBAC / 2FA
- Local Vision Agent           - Android & iOS Companion Control
- Autonomous Task Recovery     - Federated Local Fine-Tuning
```

---

## 🚀 Phase 14: Desktop GUI Overhaul & Dual-Interface Architecture (v2.0)
*Status: Active / Implementation in Progress*

### Key Objectives
- Transform ORION into an aesthetically pleasing, responsive desktop daily-driver.
- Deploy a dual-interface architecture:
  1. **CustomTkinter Desktop GUI**: Native Windows window with hardware stats, persona switches, audio visualizers, and plugin controls.
  2. **Web-Based Dashboard (FastAPI + WebSocket)**: Browser interface accessible locally (`http://localhost:8080`) or over LAN for remote PC control.

### Deliverables
- **Live Status Orb & Visualizer**: Visual representation of assistant state (`IDLE`, `LISTENING`, `PROCESSING`, `SPEAKING`, `ERROR`).
- **Voice Persona Switcher**: Instant switching between *Professional ORION*, *Friendly Mode*, and *Custom Neural Voice*.
- **Integrated Terminal & Command Palette**: Press hotkey (`Ctrl+Space`) to input text commands directly without microphone input.
- **Real-time Telemetry Dashboard**: Live CPU %, RAM GB, Battery %, active processes, and background worker threads.

---

## 🧩 Phase 15: Cloud-Connected Plugin Ecosystem & Community Skills Hub (v2.1)
*Status: Architecture Defined*

### Key Objectives
Allow community developers to create, publish, and install skills and automations without touching core ORION source code.

### Architecture
- **GitHub-Hosted Plugin Index**: A version-controlled JSON index on GitHub (`omorfarukullas/ORION-plugins`) listing official and community plugins with verified SHA-256 checksums.
- **Dynamic Plugin Manifest (`plugin.json`)**:
  ```json
  {
    "id": "spotify_controller",
    "name": "Spotify Controller",
    "version": "1.0.0",
    "author": "CommunityDev",
    "intents": ["PLAY_SPOTIFY", "SPOTIFY_PLAYLIST"],
    "dependencies": ["spotipy>=2.23.0"],
    "entrypoint": "main.py"
  }
  ```
- **Hot-Reloading Plugin Loader**: Dynamically registers intents in the NLP parser, injects regex slots, and mounts action handlers at runtime.
- **Safety Sandboxing**: Plugins declare required permissions (`NETWORK`, `FILESYSTEM_READ`, `EXECUTE_APP`). ORION prompts user authorization during installation.

---

## 🌐 Phase 16: True Cross-Platform Support — Linux & macOS (v2.2)
*Status: Planned*

### Key Objectives
Transition all Windows-specific APIs (`winreg`, Windows Registry, Windows Virtual Key codes) to a unified platform abstraction layer.

### Target Platforms
- **Linux**: Ubuntu 22.04+, Fedora, Arch Linux (`.deb`, `.rpm`, `AppImage`, Flatpak).
- **macOS**: Apple Silicon (M1/M2/M3/M4) & Intel (`.dmg`, Homebrew cask).
- **Windows**: Windows 10 & 11 (MSI / Inno Setup installer).

### Technical Implementations
- **App Discovery**: Replace `winreg` with `xdg-desktop-menu` / `/usr/share/applications` on Linux, and `/Applications` bundle scans on macOS via `platformdirs` and `shutil.which`.
- **System Sound**: SAPI5 (Windows) / `espeak-ng` or `nsss` (macOS) / `ALSA`/`PulseAudio` (Linux).
- **Process & Resource Monitoring**: Standardized cross-platform `psutil` metrics.

---

## 🧠 Phase 17: Multi-Turn Conversational Dialogue & Dynamic Slot-Filling (v2.3)
*Status: Planned*

### Key Objectives
Upgrade from single-turn command execution to contextual conversational dialogue with clarification loops.

### Deliverables
- **Slot-Filling Engine**: If an essential entity is missing (e.g., user says *"Send an email"* or *"Create a file"* without arguments), ORION transitions into a `WAITING_FOR_SLOT` state and asks: *"What should the file be named?"*.
- **10-Turn Conversation Buffer**: Extends `ConversationContext` to maintain multi-step conversational history, intent stacks, and coreference resolution.
- **Semantic Out-of-Domain Detection**: Hybrid intent parser utilizing local `sentence-transformers` embeddings to detect when a command should fall back to local Ollama LLM conversation.
- **Multilingual Support**: Auto-detect language via Whisper with localized intent datasets for Spanish, German, French, and Japanese.

---

## 🏠 Phase 18: Smart Home IoT Bridge & Media Integrations (v2.4)
*Status: Planned*

### Key Objectives
Seamlessly integrate PC voice automation with ambient smart home devices.

### Integrations
- **Home Assistant WebSocket API**: Direct local integration with Home Assistant entities (lights, switches, climate, scenes).
- **Philips Hue Local Entertainment API**: Local bridge discovery and scene orchestration.
- **Spotify Connect & Local MPD**: Voice-driven track search, volume fading, and playlist queueing.
- **MQTT / Matter Bridge**: Local MQTT publisher/subscriber for arbitrary IoT sensors and microcontrollers (ESP32, Raspberry Pi).

---

## 🔒 Phase 19: Enterprise Security Hardening & Zero-Trust Architecture (v2.5)
*Status: Planned*

### Key Objectives
Provide enterprise-ready security controls for corporate and privacy-demanding environments.

### Deliverables
- **Encrypted Database at Rest**: Migrate SQLite to `sqlcipher3` with AES-256 encryption using local machine keying (Windows DPAPI).
- **Voice Passphrase & Speaker Biometrics**: Speaker identification verification using voice embeddings (`pyannote.audio` or `SpeechBrain`) to ensure only authorized users trigger administrative or destructive commands.
- **Air-Gapped Operation Mode**: Absolute guarantee of zero internet traffic. Offline local models for STT, NLP, TTS, and LLM.
- **Tamper-Evident Audit Chains**: Cryptographic SHA-256 hash chaining of command execution logs (`logs/audit.jsonl`).

---

## 🎙️ Phase 20: Offline Neural Voice Cloning & Custom Wake-Word Studio (v3.0)
*Status: Long-Term Vision*

### Key Objectives
Complete liberation from robotic speech synthesis and fixed wake-word models.

### Deliverables
- **Custom Wake Word Studio GUI**: Built-in wizard allowing users to record 15–20 voice samples and train a custom `.onnx` openWakeWord model in under 2 minutes.
- **Coqui XTTS / Piper Offline Neural TTS**: High-fidelity, emotional, low-latency neural speech synthesis with 10-second instant voice cloning.
- **Whisper LoRA Personal Adaptation**: On-device fine-tuning adapter for Whisper acoustic features to achieve 99.9% recognition across rare accents and speech variations.
- **ORION Mobile Companion App (iOS & Android)**: React Native ambient listener that turns any smartphone into an external microphone and remote terminal for your desktop ORION node.

---

## 🤝 Contribution & Governance
Community participation is welcomed! Check out [CONTRIBUTING.md](CONTRIBUTING.md) to learn how to propose new phases, submit intent datasets, or build plugins.
