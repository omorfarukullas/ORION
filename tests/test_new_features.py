"""
tests/test_new_features.py
===========================
Unit tests for new features: Weather, Calculator, Clipboard, Ollama LLM, and Settings Panel.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

from actions import calculator, clipboard, llm, weather
from config.settings import Settings
from nlp.command_dispatcher import dispatch_action


class TestWeatherAction:
    @patch("requests.get")
    def test_weather_success(self, mock_get):
        # Mock geocoding and weather responses
        mock_geo = MagicMock()
        mock_geo.json.return_value = {
            "results": [{"latitude": 51.5, "longitude": -0.12, "name": "London"}]
        }
        mock_weather = MagicMock()
        mock_weather.json.return_value = {
            "current_weather": {"temperature": 18.5, "windspeed": 12.0, "weathercode": 1}
        }
        mock_get.side_effect = [mock_geo, mock_weather]

        res = weather.get_weather("London")
        assert "London" in res
        assert "18.5 degrees" in res

    @patch("requests.get")
    def test_weather_not_found(self, mock_get):
        mock_geo = MagicMock()
        mock_geo.json.return_value = {"results": []}
        mock_get.return_value = mock_geo

        res = weather.get_weather("NonexistentCityXYZ")
        assert "could not find weather" in res.lower()


class TestCalculatorAction:
    def test_basic_arithmetic(self):
        assert "100" in calculator.calculate("25 times 4")
        assert "400" in calculator.calculate("150 plus 250")
        assert "12" in calculator.calculate("square root of 144")

    def test_percentage_calculation(self):
        res = calculator.calculate("15 percent of 800")
        assert "120" in res

    def test_division_by_zero(self):
        res = calculator.calculate("10 / 0")
        assert "Division by zero" in res


class TestClipboardAction:
    @patch("pyperclip.paste", return_value="Hello World")
    def test_read_clipboard(self, mock_paste):
        res = clipboard.read_clipboard()
        assert "Hello World" in res

    @patch("pyperclip.copy")
    def test_copy_clipboard(self, mock_copy):
        res = clipboard.copy_to_clipboard("Test String")
        mock_copy.assert_called_once_with("Test String")
        assert "Copied" in res


class TestOllamaLLMAction:
    @patch("requests.post")
    def test_llm_success(self, mock_post):
        mock_res = MagicMock()
        mock_res.status_code = 200
        mock_res.json.return_value = {"response": "Quantum computing uses qubits."}
        mock_post.return_value = mock_res

        res = llm.ask_llm("Explain quantum computing")
        assert "Quantum computing uses qubits." in res

    @patch("requests.post")
    def test_llm_offline_fallback(self, mock_post):
        import requests
        mock_post.side_effect = requests.exceptions.ConnectionError()

        res = llm.ask_llm("What is AI?")
        assert "offline" in res.lower()


class TestDispatcherNewIntents:
    @patch("actions.weather.get_weather", return_value="In Tokyo it is 22C.")
    def test_dispatch_weather(self, mock_weather):
        res = dispatch_action("WEATHER", {"location": "Tokyo"})
        assert res == "In Tokyo it is 22C."

    @patch("actions.calculator.calculate", return_value="The answer is 42.")
    def test_dispatch_calculate(self, mock_calc):
        res = dispatch_action("CALCULATE", {"expression": "6 times 7"})
        assert res == "The answer is 42."


class TestSettingsPersistence:
    def test_settings_save_and_load(self, tmp_path):
        test_json = tmp_path / "user_settings.json"
        with patch.object(Settings, "USER_SETTINGS_PATH", test_json):
            Settings.CONFIDENCE_EXECUTE = 0.85
            Settings.TTS_RATE = 210
            Settings.save_user_settings()

            assert test_json.exists()

            # Reset values
            Settings.CONFIDENCE_EXECUTE = 0.70
            Settings.TTS_RATE = 180

            # Reload
            Settings.load_user_settings()
            assert Settings.CONFIDENCE_EXECUTE == 0.85
            assert Settings.TTS_RATE == 210

