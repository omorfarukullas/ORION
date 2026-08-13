"""
tests/test_speech_input.py
===========================
Unit tests for speech input module (Listener and SpeechToText).
"""
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from speech.listener import Listener
from speech.speech_to_text import SpeechToText


class TestListener(unittest.TestCase):
    """Test suite for speech.listener.Listener."""

    @patch("speech.listener.sd.InputStream")
    def test_listener_returns_ndarray(self, mock_input_stream):
        """Test that Listener.record() returns a numpy array."""
        listener = Listener(max_seconds=1, silence_duration=0.5)

        def mock_stream_enter(*args, **kwargs):
            # Retrieve the callback passed to InputStream
            callback = mock_input_stream.call_args[1]["callback"]
            # Simulate one chunk of non-silent audio
            chunk = np.ones((1280, 1), dtype=np.float32) * 0.1
            callback(chunk, 1280, {}, None)

        mock_input_stream.return_value.__enter__.side_effect = mock_stream_enter

        audio = listener.record()
        self.assertIsInstance(audio, np.ndarray)
        self.assertEqual(audio.dtype, np.float32)

    @patch("speech.listener.sd.InputStream")
    def test_listener_respects_max_seconds(self, mock_input_stream):
        """Test that Listener.record() respects max_seconds limit."""
        listener = Listener(max_seconds=0.1, silence_duration=5.0)

        def mock_stream_enter(*args, **kwargs):
            pass

        mock_input_stream.return_value.__enter__.side_effect = mock_stream_enter

        audio = listener.record()
        self.assertIsInstance(audio, np.ndarray)

    @patch("speech.listener.sd.InputStream")
    def test_listener_vad_stops_early(self, mock_input_stream):
        """Test that Listener stops early when silence threshold is met after speech."""
        listener = Listener(max_seconds=5.0, silence_threshold=0.05, silence_duration=0.05)

        def mock_stream_enter(*args, **kwargs):
            callback = mock_input_stream.call_args[1]["callback"]
            # 1. Speech chunk (RMS > 0.05)
            speech_chunk = np.ones((1280, 1), dtype=np.float32) * 0.1
            callback(speech_chunk, 1280, {}, None)
            # 2. Silent chunk (RMS < 0.05)
            silent_chunk = np.zeros((1280, 1), dtype=np.float32)
            callback(silent_chunk, 1280, {}, None)

        mock_input_stream.return_value.__enter__.side_effect = mock_stream_enter

        audio = listener.record()
        self.assertTrue(len(audio) > 0)


class TestSpeechToText(unittest.TestCase):
    """Test suite for speech.speech_to_text.SpeechToText."""

    @patch("speech.speech_to_text.whisper.load_model")
    def test_stt_load_model(self, mock_load_model):
        """Test that SpeechToText loads whisper model with correct params."""
        mock_model = MagicMock()
        mock_load_model.return_value = mock_model

        stt = SpeechToText(model_size="tiny", device="cpu")
        stt.load()

        mock_load_model.assert_called_once_with("tiny", device="cpu")
        self.assertIsNotNone(stt._model)

    @patch("speech.speech_to_text.whisper.load_model")
    def test_stt_transcribe_calls_model(self, mock_load_model):
        """Test that transcribe() auto-loads model and returns processed text."""
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "  Hello World  "}
        mock_load_model.return_value = mock_model

        stt = SpeechToText(model_size="base", device="cpu", language="en")
        fake_audio = np.zeros(16000, dtype=np.float32)

        result = stt.transcribe(fake_audio)

        mock_load_model.assert_called_once_with("base", device="cpu")
        self.assertEqual(mock_model.transcribe.call_count, 1)

        args, kwargs = mock_model.transcribe.call_args
        self.assertTrue(np.array_equal(args[0], fake_audio))
        self.assertEqual(kwargs.get("language"), "en")
        self.assertEqual(kwargs.get("fp16"), False)
        self.assertEqual(result, "hello world")

    def test_stt_transcribe_empty_audio(self):
        """Test that transcribe() handles empty/None audio gracefully without error."""
        stt = SpeechToText()
        stt._model = MagicMock()

        self.assertEqual(stt.transcribe(np.array([])), "")
        self.assertEqual(stt.transcribe(None), "")


if __name__ == "__main__":
    unittest.main()
