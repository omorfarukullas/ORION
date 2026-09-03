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


class TestWakeWordDetector(unittest.TestCase):
    """Test suite for speech.wake_word.WakeWordDetector."""

    def test_register_callback(self):
        """Test that register_callback correctly registers a function."""
        from speech.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="orion")
        cb = MagicMock()
        detector.register_callback(cb)
        self.assertEqual(detector._on_wake, cb)

    def test_stop_before_start(self):
        """Test that calling stop() before start() is safe."""
        from speech.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="orion")
        detector.stop()
        self.assertFalse(detector._is_running)

    def test_is_wake_word_present(self):
        """Test wake word presence check."""
        from speech.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="orion")
        detected1, cmd1 = detector._is_wake_word_present("Hey Orion")
        self.assertTrue(detected1)
        self.assertEqual(cmd1, "")

        detected2, cmd2 = detector._is_wake_word_present("Orion open notepad")
        self.assertTrue(detected2)
        self.assertEqual(cmd2, "open notepad")

        detected3, cmd3 = detector._is_wake_word_present("what time is it")
        self.assertFalse(detected3)
        self.assertEqual(cmd3, "")

        detected3b, cmd3b = detector._is_wake_word_present("Orion what time is it")
        self.assertTrue(detected3b)
        self.assertEqual(cmd3b, "what time is it")

        detected4, cmd4 = detector._is_wake_word_present("Hello world")
        self.assertFalse(detected4)
        self.assertEqual(cmd4, "")

        detected5, cmd5 = detector._is_wake_word_present("")
        self.assertFalse(detected5)
        self.assertEqual(cmd5, "")

    @patch("speech.wake_word.sd.InputStream")
    def test_wake_word_detection_triggers_callback(self, mock_input_stream):
        """Test that detecting 'orion' triggers the callback and stops the loop."""
        from speech.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="orion", chunk_seconds=0.01)
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hey Orion"}
        detector._model = mock_model

        callback_mock = MagicMock()
        detector.register_callback(callback_mock)

        def mock_stream_enter(*args, **kwargs):
            cb = mock_input_stream.call_args[1]["callback"]
            # Non-silent chunk to pass RMS check
            chunk = np.ones((1280, 1), dtype=np.float32) * 0.1
            cb(chunk, 1280, {}, None)

        mock_input_stream.return_value.__enter__.side_effect = mock_stream_enter

        detector.start()
        callback_mock.assert_called_once()
        self.assertFalse(detector._is_running)

    @patch("speech.wake_word.sd.InputStream")
    def test_wake_word_non_matching_does_not_trigger(self, mock_input_stream):
        """Test that non-wake-word transcripts do not trigger the callback."""
        from speech.wake_word import WakeWordDetector

        detector = WakeWordDetector(wake_word="orion", chunk_seconds=0.01)
        mock_model = MagicMock()
        mock_model.transcribe.return_value = {"text": "Hello world"}
        detector._model = mock_model

        callback_mock = MagicMock()
        detector.register_callback(callback_mock)

        def mock_stream_enter(*args, **kwargs):
            cb = mock_input_stream.call_args[1]["callback"]
            chunk = np.ones((1280, 1), dtype=np.float32) * 0.1
            cb(chunk, 1280, {}, None)
            detector.stop()

        mock_input_stream.return_value.__enter__.side_effect = mock_stream_enter

        detector.start()
        callback_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()


