"""Whisper transcription using faster-whisper."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from faster_whisper import WhisperModel
from PySide6.QtCore import QObject, QThread, Signal

if TYPE_CHECKING:
    pass

# Model configuration
DEFAULT_MODEL_SIZE = os.environ.get("DICTATION_MODEL", "base")
DEFAULT_DEVICE = "auto"  # auto, cpu, cuda
DEFAULT_COMPUTE_TYPE = "int8"  # int8, float16, float32

# Module-level model cache (persists for app lifetime)
_cached_model: WhisperModel | None = None
_cached_model_size: str | None = None


def get_model(model_size: str) -> WhisperModel:
    """Get or create the Whisper model (cached at module level)."""
    global _cached_model, _cached_model_size

    if _cached_model is None or _cached_model_size != model_size:
        _cached_model = WhisperModel(
            model_size,
            device=DEFAULT_DEVICE,
            compute_type=DEFAULT_COMPUTE_TYPE,
        )
        _cached_model_size = model_size

    return _cached_model


class TranscriptionWorker(QObject):
    """Worker that runs transcription in a separate thread."""

    finished = Signal(str)  # Emits transcribed text
    error = Signal(str)  # Emits error message
    progress = Signal(str)  # Emits progress updates

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._audio_path: Path | None = None
        self._model_size: str = DEFAULT_MODEL_SIZE

    def set_audio_path(self, path: Path) -> None:
        """Set the audio file to transcribe."""
        self._audio_path = path

    def set_model_size(self, size: str) -> None:
        """Set the Whisper model size."""
        self._model_size = size

    def run(self) -> None:
        """Perform transcription - called from worker thread."""
        if self._audio_path is None:
            self.error.emit("No audio file specified")
            return

        try:
            self.progress.emit("Loading model...")

            # Get cached model
            model = get_model(self._model_size)

            self.progress.emit("Transcribing...")

            # Transcribe
            segments, info = model.transcribe(
                str(self._audio_path),
                beam_size=5,
                vad_filter=True,  # Voice activity detection
            )

            # Collect all text
            text_parts = [segment.text for segment in segments]
            full_text = " ".join(text_parts).strip()

            # Clean up temp file
            self._audio_path.unlink(missing_ok=True)

            self.finished.emit(full_text)

        except Exception as e:
            self.error.emit(str(e))


class Transcriber(QObject):
    """Manages transcription with background threading."""

    transcription_started = Signal()
    transcription_finished = Signal(str)  # Emits transcribed text
    transcription_error = Signal(str)
    transcription_progress = Signal(str)

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._thread: QThread | None = None
        self._worker: TranscriptionWorker | None = None
        self._model_size: str = DEFAULT_MODEL_SIZE

    def set_model_size(self, size: str) -> None:
        """Set the Whisper model size."""
        self._model_size = size

    def transcribe(self, audio_path: Path) -> None:
        """Start transcription in background thread."""
        # Clean up any previous thread
        self._cleanup_thread()

        # Create worker and thread
        self._thread = QThread()
        self._worker = TranscriptionWorker()
        self._worker.set_audio_path(audio_path)
        self._worker.set_model_size(self._model_size)
        self._worker.moveToThread(self._thread)

        # Connect signals
        self._thread.started.connect(self._worker.run)
        self._worker.finished.connect(self._on_finished)
        self._worker.error.connect(self._on_error)
        self._worker.progress.connect(self.transcription_progress.emit)
        self._worker.finished.connect(self._thread.quit)
        self._worker.error.connect(self._thread.quit)

        # Start
        self.transcription_started.emit()
        self._thread.start()

    def _on_finished(self, text: str) -> None:
        """Handle transcription completion."""
        self.transcription_finished.emit(text)
        self._cleanup_thread()

    def _on_error(self, error: str) -> None:
        """Handle transcription error."""
        self.transcription_error.emit(error)
        self._cleanup_thread()

    def _cleanup_thread(self) -> None:
        """Clean up thread and worker."""
        if self._thread is not None:
            if self._thread.isRunning():
                self._thread.quit()
                self._thread.wait()
            self._thread.deleteLater()
            self._thread = None
        if self._worker is not None:
            self._worker.deleteLater()
            self._worker = None
