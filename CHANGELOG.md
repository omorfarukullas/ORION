# Changelog

All notable changes to **ORION** will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-09-04

### Added
- **Web-Based Dashboard & API**:
  - FastAPI backend serving responsive modern glassmorphic web dashboard on `http://127.0.0.1:8080`.
  - WebSocket `/ws` stream for real-time assistant state and hardware telemetry broadcast.
  - REST endpoints for direct text command injection, history audit, and settings management.
- **Selectable Voice Personas**:
  - `speech/personas.py` introducing "Professional ORION", "Friendly Mode", and extensible "Coqui TTS / Custom Voice Clone".
  - Dynamic rate, pitch, and phrasing adaptation hooks.
- **Cloud Plugin Registry**:
  - GitHub-hosted plugin index fetching with local offline fallback.
  - `plugins/registry.py` and `plugins/loader.py` for dynamic intent and action mounting.
- **Packaging & Deployment Infrastructure**:
  - One-click Windows installer pipeline using PyInstaller and Inno Setup (`scripts/orion.spec`, `scripts/orion_installer.iss`, `scripts/build_installer.ps1`).
  - Standard Python distribution setup (`setup.py`, `pyproject.toml`, `MANIFEST.in`).
  - Containerization files (`Dockerfile`, `docker-compose.yml`) for headless / home-assistant deployments.
  - GitHub Actions CI/CD workflows for automated multi-version testing, linting, and release artifact generation.
- **Long-Term Roadmap**:
  - `ROADMAP.md` mapping out future development through Phases 14 to 20 (cross-platform, multi-turn dialogue, IoT bridges, security hardening, voice cloning).

### Changed
- `gui/dashboard.py`: Added 1-click Web UI browser launch button and interactive Plugins management tab.
- `gui/settings_panel.py`: Added Voice Persona dropdown selector and updated persistence handlers.
- `speech/text_to_speech.py`: Integrated persona styling into speech synthesis loop.
- `app.py`: Added background daemon thread initialization for Web Dashboard API server.

---

## [1.0.0] - 2026-09-02
- Initial release featuring local Whisper speech recognition, openWakeWord standby, 34-intent NLP classification, safety gating, and CustomTkinter desktop interface.
