"""Dictation controller exposing recording/transcription to QML."""

from __future__ import annotations

from enum import IntEnum
from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Signal, Slot

from dictation.audio import AudioRecorder
from dictation.transcriber import Transcriber

if TYPE_CHECKING:
    from PySide6.QtGui import QClipboard


class DictationState(IntEnum):
    """Dictation state machine states."""

    IDLE = 0
    RECORDING = 1
    TRANSCRIBING = 2
    COMPLETED = 3
    ERROR = 4


class DictationController(QObject):
    """Controller for dictation functionality, exposed to QML."""

    # Signals for QML binding
    stateChanged = Signal()
    transcribedTextChanged = Signal()
    errorMessageChanged = Signal()
    progressMessageChanged = Signal()

    def __init__(
        self,
        clipboard: QClipboard | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._state: DictationState = DictationState.IDLE
        self._transcribed_text: str = ""
        self._error_message: str = ""
        self._progress_message: str = ""
        self._clipboard = clipboard

        # Components
        self._recorder = AudioRecorder()
        self._transcriber = Transcriber(self)

        # Connect transcriber signals
        self._transcriber.transcription_finished.connect(
            self._on_transcription_finished
        )
        self._transcriber.transcription_error.connect(self._on_transcription_error)
        self._transcriber.transcription_progress.connect(
            self._on_transcription_progress
        )

    # --- Properties for QML ---

    @Property(int, notify=stateChanged)
    def state(self) -> int:
        """Current dictation state."""
        return int(self._state)

    @Property(str, notify=transcribedTextChanged)
    def transcribedText(self) -> str:
        """The transcribed text."""
        return self._transcribed_text

    @Property(str, notify=errorMessageChanged)
    def errorMessage(self) -> str:
        """Error message if any."""
        return self._error_message

    @Property(str, notify=progressMessageChanged)
    def progressMessage(self) -> str:
        """Progress message during transcription."""
        return self._progress_message

    @Property(bool, notify=stateChanged)
    def isRecording(self) -> bool:
        """True if currently recording."""
        return self._state == DictationState.RECORDING

    @Property(bool, notify=stateChanged)
    def isTranscribing(self) -> bool:
        """True if currently transcribing."""
        return self._state == DictationState.TRANSCRIBING

    @Property(bool, notify=stateChanged)
    def isIdle(self) -> bool:
        """True if idle and ready to record."""
        return self._state == DictationState.IDLE

    # --- Slots for QML ---

    @Slot()
    def toggle(self) -> None:
        """Toggle recording on/off."""
        if self._state == DictationState.IDLE:
            self._start_recording()
        elif self._state == DictationState.RECORDING:
            self._stop_recording()
        elif self._state == DictationState.COMPLETED:
            # Reset and start new recording
            self._reset()
            self._start_recording()
        elif self._state == DictationState.ERROR:
            # Reset from error state
            self._reset()
        # Ignore toggle during TRANSCRIBING

    @Slot()
    def copyToClipboard(self) -> None:
        """Copy transcribed text to clipboard."""
        if self._clipboard is not None and self._transcribed_text:
            self._clipboard.setText(self._transcribed_text)

    @Slot()
    def reset(self) -> None:
        """Reset to idle state."""
        self._reset()

    # --- Internal methods ---

    def _start_recording(self) -> None:
        """Start audio recording."""
        self._error_message = ""
        self._transcribed_text = ""
        self._progress_message = ""
        self._state = DictationState.RECORDING
        self.stateChanged.emit()
        self.transcribedTextChanged.emit()
        self.errorMessageChanged.emit()

        try:
            self._recorder.start()
        except Exception as e:
            self._error_message = f"Failed to start recording: {e}"
            self._state = DictationState.ERROR
            self.stateChanged.emit()
            self.errorMessageChanged.emit()

    def _stop_recording(self) -> None:
        """Stop recording and start transcription."""
        try:
            audio_path = self._recorder.stop()
            self._state = DictationState.TRANSCRIBING
            self._progress_message = "Starting transcription..."
            self.stateChanged.emit()
            self.progressMessageChanged.emit()

            # Start transcription
            self._transcriber.transcribe(audio_path)

        except Exception as e:
            self._error_message = f"Failed to stop recording: {e}"
            self._state = DictationState.ERROR
            self.stateChanged.emit()
            self.errorMessageChanged.emit()

    def _on_transcription_finished(self, text: str) -> None:
        """Handle transcription completion."""
        self._transcribed_text = text
        self._progress_message = ""
        self._state = DictationState.COMPLETED
        self.stateChanged.emit()
        self.transcribedTextChanged.emit()
        self.progressMessageChanged.emit()

        # Auto-copy to clipboard
        self.copyToClipboard()

    def _on_transcription_error(self, error: str) -> None:
        """Handle transcription error."""
        self._error_message = error
        self._progress_message = ""
        self._state = DictationState.ERROR
        self.stateChanged.emit()
        self.errorMessageChanged.emit()
        self.progressMessageChanged.emit()

    def _on_transcription_progress(self, message: str) -> None:
        """Handle progress updates."""
        self._progress_message = message
        self.progressMessageChanged.emit()

    def _reset(self) -> None:
        """Reset to idle state."""
        self._transcribed_text = ""
        self._error_message = ""
        self._progress_message = ""
        self._state = DictationState.IDLE
        self.stateChanged.emit()
        self.transcribedTextChanged.emit()
        self.errorMessageChanged.emit()
        self.progressMessageChanged.emit()
