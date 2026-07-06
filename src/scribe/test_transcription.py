import tempfile
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import patch

from scribe.transcription import (
    DEFAULT_TRANSCRIPTION_MODEL,
    MAX_AUDIO_SIZE_MB,
    TranscriptionError,
    _build_multipart_body,
    build_transcription_payload,
    parse_transcription_response,
    transcribe_audio,
    validate_audio_file,
)


class ValidateAudioFileTests(TestCase):
    def test_validate_audio_file_rejects_missing_path(self):
        with self.assertRaisesRegex(TranscriptionError, "not found"):
            validate_audio_file("/nonexistent/file.wav")

    def test_validate_audio_file_rejects_too_large_file(self):
        with patch.object(Path, "exists", return_value=True), patch.object(Path, "is_file", return_value=True), patch.object(Path, "stat") as mock_stat:
            mock_stat.return_value.st_size = int((MAX_AUDIO_SIZE_MB + 1) * 1024 * 1024)

            with self.assertRaisesRegex(TranscriptionError, "too large"):
                validate_audio_file("/some/large/file.wav")


class TranscriptionPayloadTests(TestCase):
    def test_build_transcription_payload_uses_default_model(self):
        payload = build_transcription_payload(DEFAULT_TRANSCRIPTION_MODEL)

        self.assertEqual(payload, {"model": DEFAULT_TRANSCRIPTION_MODEL})


class ParseTranscriptionResponseTests(TestCase):
    def test_parse_transcription_response_extracts_text_and_metadata(self):
        response_body = """
        {
            "text": "Bonjour tout le monde.",
            "language": "fr",
            "duration": 12.3,
            "segments": [{"id": 1}]
        }
        """

        result = parse_transcription_response(response_body)

        self.assertEqual(result["text"], "Bonjour tout le monde.")
        self.assertEqual(result["language"], "fr")
        self.assertEqual(result["duration"], 12.3)
        self.assertEqual(result["segments"], [{"id": 1}])


class MultipartBodyTests(TestCase):
    def test_build_multipart_body_contains_model_and_filename(self):
        body = _build_multipart_body("BOUNDARY", "model-x", "audio.wav", b"abc")

        self.assertIn(b'name="model"', body)
        self.assertIn(b"model-x", body)
        self.assertIn(b'filename="audio.wav"', body)


class TranscriptionTests(TestCase):
    def test_transcribe_audio_happy_path(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "sample.wav"
            path.write_bytes(b"abc")

            fake_response = '{"text":"Hello world","language":"en","duration":2.0,"segments":[]}'

            class DummyResponse:
                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

                def read(self):
                    return fake_response.encode("utf-8")

            with patch("scribe.transcription.request.urlopen", return_value=DummyResponse()):
                result = transcribe_audio(str(path), api_key="key", model="model-x")

            self.assertEqual(result["text"], "Hello world")


if __name__ == "__main__":
    main()
