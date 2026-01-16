"""Audio recording functionality using sounddevice."""

from __future__ import annotations

import tempfile
import wave
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np
import sounddevice as sd
from scipy.signal import butter, sosfilt

if TYPE_CHECKING:
    from numpy.typing import NDArray

# Audio settings
SAMPLE_RATE = 16000  # 16kHz - optimal for Whisper
CHANNELS = 1  # Mono
DTYPE = np.float32  # sounddevice default
BANDPASS_LOW = 80  # Hz - removes low-frequency rumble
BANDPASS_HIGH = 7000  # Hz - removes high-frequency hiss


def apply_bandpass_filter(
    audio: NDArray[np.float32], sample_rate: int
) -> NDArray[np.float32]:
    """Apply bandpass filter to isolate speech frequencies (80Hz - 7kHz)."""
    sos = butter(
        4, [BANDPASS_LOW, BANDPASS_HIGH], btype="band", fs=sample_rate, output="sos"
    )
    filtered = np.asarray(sosfilt(sos, audio), dtype=np.float32)
    return filtered


class AudioRecorder:
    """Records audio from the default microphone."""

    def __init__(self) -> None:
        self._frames: list[NDArray[np.float32]] = []
        self._stream: sd.InputStream | None = None
        self._is_recording: bool = False

    def start(self) -> None:
        """Start recording audio."""
        self._frames = []
        self._is_recording = True
        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> Path:
        """Stop recording and return path to temporary WAV file."""
        self._is_recording = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Handle case where no audio was recorded
        if not self._frames:
            # Create empty audio data
            audio_data = np.array([], dtype=np.float32)
        else:
            # Concatenate all frames and apply bandpass filter
            audio_data = np.concatenate(self._frames, axis=0)
            audio_data = apply_bandpass_filter(audio_data, SAMPLE_RATE)

        # Save to temporary WAV file
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = Path(temp_file.name)
        temp_file.close()

        # Write WAV file (convert float32 to int16 for WAV)
        if len(audio_data) > 0:
            audio_int16 = (audio_data * 32767).astype(np.int16)
        else:
            audio_int16 = np.array([], dtype=np.int16)

        with wave.open(str(temp_path), "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_int16.tobytes())

        return temp_path

    def _audio_callback(
        self,
        indata: NDArray[np.float32],
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        """Callback for audio stream - called from separate thread."""
        if self._is_recording:
            self._frames.append(indata.copy())

    @property
    def is_recording(self) -> bool:
        """Return True if currently recording."""
        return self._is_recording
