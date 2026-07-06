from __future__ import annotations

import json
import uuid
from contextlib import suppress
from pathlib import Path
from typing import Any, Dict
from urllib import error, request


GROQ_TRANSCRIPTION_URL = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_TRANSCRIPTION_MODEL = "whisper-large-v3-turbo"
MAX_AUDIO_SIZE_MB = 25


class TranscriptionError(Exception):
    """Raised when transcription cannot proceed."""


def validate_audio_file(file_path: str) -> Path:
    """Validate that the audio file exists and stays within the size limit."""
    audio_path = Path(file_path)
    if not audio_path.exists():
        raise TranscriptionError(f"Audio file not found: {file_path}")
    if not audio_path.is_file():
        raise TranscriptionError(f"Path is not a file: {file_path}")

    file_size_mb = audio_path.stat().st_size / (1024 * 1024)
    if file_size_mb > MAX_AUDIO_SIZE_MB:
        raise TranscriptionError(
            f"Audio file too large: {file_size_mb:.1f}MB (max {MAX_AUDIO_SIZE_MB}MB)"
        )

    return audio_path


def build_transcription_payload(model: str = DEFAULT_TRANSCRIPTION_MODEL) -> Dict[str, str]:
    """Build the small payload sent to Groq."""
    if not model:
        raise TranscriptionError("Transcription model is required")
    return {"model": model}


def parse_transcription_response(response_body: str) -> Dict[str, Any]:
    try:
        result = json.loads(response_body)
    except json.JSONDecodeError as exc:
        raise TranscriptionError("Invalid transcription response JSON") from exc

    if "text" not in result:
        raise TranscriptionError("Groq response does not contain transcription text.")

    transcription: Dict[str, Any] = {
        "text": result["text"],
        "language": result.get("language", "unknown"),
        "duration": result.get("duration"),
    }
    if "segments" in result:
        transcription["segments"] = result["segments"]
    return transcription


def _build_multipart_body(boundary: str, model: str, filename: str, file_content: bytes) -> bytes:
    lines = [
        f"--{boundary}",
        'Content-Disposition: form-data; name="model"',
        "",
        model,
        f"--{boundary}",
        f'Content-Disposition: form-data; name="file"; filename="{filename}"',
        "Content-Type: application/octet-stream",
        "",
    ]
    return (
        "\r\n".join(lines).encode("utf-8")
        + b"\r\n"
        + file_content
        + f"\r\n--{boundary}--\r\n".encode("utf-8")
    )


def transcribe_audio(
    file_path: str,
    api_key: str,
    model: str = DEFAULT_TRANSCRIPTION_MODEL,
    timeout: int = 30,
) -> Dict[str, Any]:
    """Transcribe an audio file through Groq."""
    if not api_key:
        raise TranscriptionError("GROQ API key is required")

    audio_path = validate_audio_file(file_path)
    payload = build_transcription_payload(model)

    with audio_path.open("rb") as audio_file:
        boundary = uuid.uuid4().hex
        file_content = audio_file.read()
        form_data = _build_multipart_body(
            boundary,
            payload["model"],
            audio_path.name,
            file_content,
        )
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }
        http_request = request.Request(
            GROQ_TRANSCRIPTION_URL,
            data=form_data,
            headers=headers,
            method="POST",
        )
        try:
            with request.urlopen(http_request, timeout=timeout) as response:
                response_body = response.read().decode("utf-8")
        except error.HTTPError as exc:
            error_message = exc.reason
            with suppress(Exception):
                error_payload = json.loads(exc.read().decode("utf-8"))
                error_message = error_payload.get("error", {}).get("message", error_message)
            raise TranscriptionError(f"Groq API error: {error_message}") from exc
        except error.URLError as exc:
            raise TranscriptionError("Failed to connect to Groq API.") from exc
        except TimeoutError as exc:
            raise TranscriptionError("Transcription request timed out.") from exc

    return parse_transcription_response(response_body)
