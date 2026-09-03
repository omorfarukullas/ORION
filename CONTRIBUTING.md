# Contributing to ORION

Thank you for your interest in making ORION better! We welcome contributions from the community, whether bug fixes, new intents, plugin integrations, performance optimizations, or documentation.

---

## 🛠️ Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/ORION.git
   cd ORION
   ```

2. **Create and activate a virtual environment**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install development dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify the test suite**:
   ```powershell
   python -m pytest tests/ -v
   ```

---

## 🧩 Adding a New Intent / Action

To add a new capability to ORION:
1. **Add training samples**: Append labeled training sentences to `data/intents.csv`.
2. **Retrain the classifier**:
   ```powershell
   python nlp/train_classifier.py
   ```
3. **Add the action handler**: Implement the logic in `actions/<module>.py`.
4. **Wire the router**: Update `nlp/command_dispatcher.py` to route the new intent.
5. **Add unit tests**: Write unit tests in `tests/test_actions.py` or a dedicated test file.

---

## 🎨 Building a Plugin

Plugins allow extending ORION without modifying core code.
Create a folder under `plugins/<plugin_name>/` with a `plugin.json` manifest:
```json
{
  "id": "my_plugin",
  "name": "My Custom Plugin",
  "version": "1.0.0",
  "description": "What my plugin does",
  "entrypoint": "main.py"
}
```
And expose a `register_handlers()` function in `main.py`:
```python
def register_handlers():
    return {
        "MY_CUSTOM_INTENT": handle_my_intent
    }
```

---

## 📋 Pull Request Checklist

Before submitting your pull request, please ensure:
- [ ] All tests pass cleanly (`python -m pytest tests/`).
- [ ] Code follows PEP 8 conventions.
- [ ] Documentation and comments are updated if public interfaces changed.
- [ ] Meaningful commit messages are used.
