"""
speech/listener.py
==================
Handles microphone recording after wake-word detection. Captures audio
until silence is detected via energy-based VAD or ``max_seconds`` elapses,
then returns the raw audio buffer for transcription.
"""
from __future__ import annotations
import time
import numpy as np
import sounddevice as sd
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class Listener:
    """
    Records a single command from the microphone.

    Triggered by :class:`speech.wake_word.WakeWordDetector` after wake
    word confirmation. Uses ``sounddevice`` for cross-platform mic input
    at 16 kHz (required by both openWakeWord and Whisper).
    """

    def __init__(
        self,
        sample_rate: int = Settings.SAMPLE_RATE,
        max_seconds: int = Settings.RECORD_SECONDS,
        silence_threshold: float = Settings.VAD_SILENCE_THRESHOLD,
        silence_duration: float = Settings.VAD_SILENCE_DURATION,
        chunk_size: int = Settings.CHUNK_SIZE,
    ) -> None:
        """
        Args:
            sample_rate:       Audio sample rate in Hz (16 000 for Whisper).
            max_seconds:       Maximum recording duration before auto-stop.
            silence_threshold: RMS amplitude below which audio is silent.
            silence_duration:  Seconds of consecutive silence to trigger stop.
            chunk_size:        Frames per buffer chunk.
        """
        self.sample_rate = sample_rate
        self.max_seconds = max_seconds
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.chunk_size = chunk_size

    def record(self) -> np.ndarray:
        """
        Record audio from the default microphone.

        Returns:
            Mono float32 numpy array at ``self.sample_rate`` Hz.
        """
        logger.info("Starting microphone recording...")
        recorded_chunks: list[np.ndarray] = []
        silence_start_time: float | None = None
        has_speech_started = False
        start_time = time.time()

        def audio_callback(indata: np.ndarray, frames: int, time_info: dict, status: sd.CallbackFlags) -> None:
            if status:
                logger.warning(f"Audio callback status warning: {status}")
            recorded_chunks.append(indata.copy())

        with sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=self.chunk_size,
            callback=audio_callback,
        ):
            while True:
                elapsed_time = time.time() - start_time
                if elapsed_time >= self.max_seconds:
                    logger.info(f"Reached max recording time ({self.max_seconds}s). Stopping.")
                    break

                if recorded_chunks:
                    recent_chunk = recorded_chunks[-1]
                    rms = float(np.sqrt(np.mean(recent_chunk**2)))

                    if rms >= self.silence_threshold:
                        has_speech_started = True
                        silence_start_time = None
                    else:
                        if has_speech_started:
                            if silence_start_time is None:
                                silence_start_time = time.time()
                            elif time.time() - silence_start_time >= self.silence_duration:
                                logger.info(
                                    f"Silence detected for {self.silence_duration}s after speech. Stopping recording."
                                )
                                break

                time.sleep(0.02)

        if recorded_chunks:
            audio = np.concatenate(recorded_chunks, axis=0).flatten()
        else:
            audio = np.array([], dtype=np.float32)

        logger.info(f"Recording finished. Captured {len(audio) / self.sample_rate:.2f}s of audio.")
        return audio
