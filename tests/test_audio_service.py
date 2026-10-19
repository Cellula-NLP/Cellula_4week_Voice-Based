"""Unit tests for the AudioService."""
import pytest
from unittest.mock import MagicMock
from app.services.audio_service import AudioService
from app.core.exceptions import STTError


def test_audio_transcription_success():
    # 1. Setup Mock STT
    mock_stt = MagicMock()
    mock_stt.transcribe.return_value = ("Show me total sales", "en")

    # 2. Initialize Service
    service = AudioService(stt_provider=mock_stt)

    # 3. Execute
    transcript, lang = service.process_audio("fake_audio_path.wav")

    # 4. Assert
    assert transcript == "Show me total sales"
    assert lang == "en"
    mock_stt.transcribe.assert_called_once_with("fake_audio_path.wav")


def test_audio_transcription_arabic_success():
    mock_stt = MagicMock()
    mock_stt.transcribe.return_value = ("أظهر لي إجمالي المبيعات", "ar")

    service = AudioService(stt_provider=mock_stt)
    transcript, lang = service.process_audio("arabic_audio.wav")

    assert transcript == "أظهر لي إجمالي المبيعات"
    assert lang == "ar"


def test_audio_transcription_empty_speech():
    # Mock STT returning empty text (silence or background noise)
    mock_stt = MagicMock()
    mock_stt.transcribe.return_value = ("", "en")

    service = AudioService(stt_provider=mock_stt)

    with pytest.raises(STTError, match="Could not detect any speech in the audio."):
        service.process_audio("silent_audio.wav")