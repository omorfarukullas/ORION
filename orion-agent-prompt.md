# ORION — AI Agent Build Prompt

Copy everything below into your AI coding agent (e.g. Claude Code) as the
starting instruction. It's written so the agent can pick it up cold, build
incrementally, and check in with you at the right moments instead of
sprinting to a half-working V3.

---

## SYSTEM / TASK PROMPT FOR THE AGENT

You are building **ORION** (Operational Responsive Intelligent Orchestration
Network) — a local, voice-controlled PC assistant in Python. It runs in the
background, wakes on a wake word, transcribes a spoken command, classifies
intent + extracts entities with a real ML pipeline, plans multi-step tasks,
executes them through safety-gated PC automation functions, and replies with
synthesized speech.

Read this entire prompt before writing any code. Follow the **Operating
Rules** for every phase, then execute the **Build Plan** phase by phase.

### Non-negotiable operating rules

1. **Build in the phase order given below. Do not skip ahead.** Each phase
   must run end-to-end and be demoed/verified before the next one starts.
   If you think a later feature would be easy to bolt on early, don't —
   note it and move on.
2. **Stop and ask me before starting each new phase.** Give a one-paragraph
   summary of what the previous phase does, how to run/test it, and any
   decisions you made (library choices, model size, etc.). Wait for my
   go-ahead.
3. **Safety system is mandatory, not optional polish.** Any action that
   deletes, overwrites, shuts down/restarts, or runs an arbitrary shell
   command must go through a confirmation step before execution, exactly as
   described in Phase 9. Never implement a raw "run this shell command"
   intent. Never implement registry edits or system configuration changes.
4. **Local-first.** Wake-word detection and speech-to-text must run
   locally (openWakeWord + a local Whisper model) — never stream raw mic
   audio to a cloud API continuously. It's fine if a *specific* command
   later calls an external API, but always with the user's command as the
   trigger, never as background listening.
5. **Confidence thresholds gate execution**, not just get logged:
   `>80%` → execute, `50–80%` → ask for confirmation, `<50%` → ask for
   clarification. Wire this in from Phase 6 onward; don't leave it as a
   TODO.
6. **Modular architecture from day one** — use the directory structure in
   the Project Architecture section below, even in Phase 1 when most
   folders are still empty stubs. Don't collapse everything into one
   `app.py` "for now."
7. **Write a test for each action function** (applications, browser,
   files, system, media, screenshots) as you build it in Phase 8, not
   retroactively.
8. **Every phase updates the README** with what now works and how to run
   it, so the project is demoable at any checkpoint, not just at the end.
9. **When something in the plan is ambiguous or you have to choose between
   libraries/approaches, state the trade-off in 2-3 sentences and pick
   one** rather than stalling on it — but flag it in your phase summary so
   I can override the choice.

### Target platform

Ask me at the start of Phase 1 which OS I'm developing on (Windows /
macOS / Linux) if it's not obvious from context, since app-launching,
volume control, and screenshot APIs differ by platform. Default to
cross-platform libraries where they exist (`psutil`, `pyautogui`,
`webbrowser`) and isolate anything OS-specific behind a small adapter in
`actions/`.

---

## PROJECT ARCHITECTURE

```
ORION/
├── app.py
├── config/
│   ├── settings.py
│   ├── applications.json
│   └── commands.json
├── data/
│   ├── intents.csv
│   └── training_data.json
├── models/
│   ├── intent_classifier.pkl
│   └── tfidf_vectorizer.pkl
├── speech/
│   ├── wake_word.py
│   ├── listener.py
│   ├── speech_to_text.py
│   └── text_to_speech.py
├── nlp/
│   ├── preprocessing.py
│   ├── intent_classifier.py
│   ├── entity_extractor.py
│   └── command_parser.py
├── planner/
│   ├── task_planner.py
│   └── context.py
├── actions/
│   ├── applications.py
│   ├── browser.py
│   ├── files.py
│   ├── system.py
│   ├── media.py
│   └── screenshots.py
├── security/
│   ├── permissions.py
│   ├── confirmation.py
│   └── command_validator.py
├── database/
│   └── database.py
├── gui/
│   ├── dashboard.py
│   ├── status.py
│   └── history.py
├── utils/
│   ├── logger.py
│   └── helpers.py
├── tests/
│   ├── test_intent.py
│   ├── test_entities.py
│   ├── test_actions.py
│   └── test_security.py
├── requirements.txt
├── README.md
└── .gitignore
```

### Tech stack

- **Core:** Python 3.11+
- **Speech:** local Whisper (start with a small model), `sounddevice`, `openWakeWord`
- **ML/NLP:** scikit-learn (TF-IDF + Logistic Regression for intents), NumPy, Pandas
- **PC automation:** `pyautogui`, `psutil`, `pathlib`, `subprocess` (only for allow-listed actions), `webbrowser`
- **Audio out:** `pyttsx3`
- **GUI:** CustomTkinter
- **Storage:** SQLite

---

## BUILD PLAN (execute phase by phase, checking in after each)

**Phase 1 — Project setup.** Scaffold the full directory tree above (empty
stub files where needed), virtual environment, `requirements.txt`, git
repo with `.gitignore`, and a `config/settings.py`. Success criterion:
`python app.py` runs without error (even if it just prints "ORION
initialized").

**Phase 2 — Text-to-speech.** Wire up `pyttsx3` in
`speech/text_to_speech.py`. Success criterion: ORION speaks "Hello. I am
ORION." No ML yet.

**Phase 3 — Speech recognition.** Build the mic → local Whisper → text
pipeline in `speech/speech_to_text.py` and `speech/listener.py`. Success
criterion: saying "Hello ORION" prints `hello orion`.

**Phase 4 — Wake word.** Integrate `openWakeWord` in `speech/wake_word.py`
so ORION idles in standby, wakes on "ORION," and only then starts
recording a command. Success criterion: the standby → wake → listen loop
works reliably a few times in a row.

**Phase 5 — Basic command engine.** Hard-code handling (no ML yet) for:
time, date, open Chrome, open VS Code, Google search, YouTube search,
screenshot. This is the first end-to-end "hear it, do it, say it" loop.

**Phase 6 — ML intent classifier.** Build `data/intents.csv` /
`training_data.json` covering the ~20 intents listed below, preprocess
text in `nlp/preprocessing.py`, train TF-IDF + Logistic Regression in
`nlp/intent_classifier.py`, evaluate it, and save
`models/intent_classifier.pkl` + `models/tfidf_vectorizer.pkl`. Wire in
the confidence thresholds from rule 5 above.

Initial intents:
- Application: `OPEN_APP`, `CLOSE_APP`
- Web: `OPEN_WEBSITE`, `WEB_SEARCH`, `YOUTUBE_SEARCH`
- System: `SYSTEM_CPU`, `SYSTEM_RAM`, `SYSTEM_BATTERY`, `SYSTEM_INFO`
- Files: `CREATE_FOLDER`, `CREATE_FILE`, `FIND_FILE`, `RENAME_FILE`, `DELETE_FILE`
- Media: `PLAY_MEDIA`, `PAUSE_MEDIA`, `NEXT_TRACK`, `PREVIOUS_TRACK`, `VOLUME_UP`, `VOLUME_DOWN`, `MUTE`
- Utility: `TIME`, `DATE`, `SCREENSHOT`

**Phase 7 — Entity extraction.** Rule-based extraction in
`nlp/entity_extractor.py` (e.g. "Open Chrome" → intent `OPEN_APP`, entity
`Chrome`). Combine with the classifier in `nlp/command_parser.py`.

**Phase 8 — PC automation.** Implement each `actions/*.py` module listed
in the architecture (applications, browser, files, system, media,
screenshots) as small, individually-testable functions. Write the
corresponding test in `tests/test_actions.py` as each module lands.

**Phase 9 — Security.** Implement `security/command_validator.py`
(allow-list of safe vs. potentially-destructive vs. unsupported actions),
`security/confirmation.py` (asks "You're asking me to X. Should I
continue?" for destructive actions and waits for explicit yes),
`security/permissions.py`, and logging. Categories:
- **Safe → execute immediately:** open app, search, check CPU, screenshot, etc.
- **Potentially destructive → confirmation required:** delete file/folder, shutdown, restart.
- **Dangerous → do not implement in V1 at all:** arbitrary terminal commands, registry edits, system configuration changes.

**Phase 10 — GUI.** Build the CustomTkinter dashboard (`gui/dashboard.py`,
`status.py`, `history.py`) showing online status, listening indicator,
last command with intent/entity/confidence, recent command history, and
live CPU/RAM/battery.

**Phase 11 — Context + memory.** Add `planner/context.py` (tracks
`last_intent`, `last_entity`, `last_application` so "search for X" after
"open Chrome" resolves correctly) and `database/database.py` (SQLite) for
simple persisted memory like "remember that my project folder is on
Desktop."

**Phase 12 — Final polish.** Full pass on tests, README (setup, usage,
architecture diagram, known limitations), and a short demo script showing
the multi-step example: *"ORION, open Chrome and search YouTube for Python
tutorials."*

---

## MULTI-STEP TASK PLANNING (build this into Phase 6+ intent handling and Phase 11 planner)

A command like *"Open Chrome, go to YouTube, and search for Python
tutorials"* should be decomposed by `planner/task_planner.py` into an
ordered list of single-intent tasks and executed sequentially, with each
step's result feeding ORION's final spoken confirmation (e.g. "Done. I
found the results.").

## DEMO COMMANDS TO VALIDATE AGAINST

Use these as your acceptance tests at the end of Phase 12:

- "ORION, open Visual Studio Code."
- "ORION, search Google for machine learning projects."
- "ORION, search YouTube for Python tutorials."
- "ORION, how much RAM am I using?"
- "ORION, create a folder called AI Projects."
- "ORION, take a screenshot."
- "ORION, increase the volume."
- "ORION, open Chrome and search YouTube for Python tutorials." (multi-step)
- "ORION, remember that my project folder is on Desktop." → later: "ORION, open my project folder." (memory)
- "ORION, delete my project folder." → must trigger confirmation, not immediate deletion.

## OUT OF SCOPE FOR THIS BUILD

Do not implement, even as a stretch goal, without explicit sign-off:
screen/camera vision, LLM-based reasoning replacing the intent classifier,
or "computer-use" style autonomous multi-app workflows (e.g. "download and
install Python for me"). These are V3-territory and introduce safety and
reliability problems this build isn't scoped to handle.

---

Begin with Phase 1. Confirm the target OS with me if unclear, scaffold the
project, and report back before touching Phase 2.
