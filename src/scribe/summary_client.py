"""Minimal Groq chat client for producing structured summaries from transcription.

This client is intentionally small so we can add it in one defensible commit.
"""

import json
from typing import Dict
from urllib import error, parse, request


GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
DEFAULT_CHAT_MODEL = "gpt-4o-mini"  # placeholder, choose appropriate model in README


class SummaryError(Exception):
    pass


def build_chat_payload(system_prompt: str, transcription: str, model: str = DEFAULT_CHAT_MODEL) -> Dict:
    """Build the minimal chat payload expected by the Groq chat endpoint.

    We send a system message (the prompt stored on disk) and a user message
    containing the transcription.
    """
    return {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcription},
        ],
        "temperature": 0.0,
    }


def parse_chat_response(body: str) -> str:
    """Extract the assistant text from a Groq/OpenAI-like response body.

    Returns the assistant message content as a string.
    Raises SummaryError on malformed responses.
    """
    data = json.loads(body)
    # expect structure: { choices: [ { message: { content: "..." } } ] }
    try:
        choices = data["choices"]
        if not choices:
            raise KeyError("no choices")
        message = choices[0]["message"]
        content = message["content"]
        return content
    except Exception as exc:
        raise SummaryError(f"Invalid chat response: {exc}") from exc


def summarize_transcription(system_prompt: str, transcription: str, api_key: str, model: str = DEFAULT_CHAT_MODEL, timeout: int = 30) -> str:
    """Call Groq chat completions and return the assistant text.

    Uses urllib to avoid adding runtime dependencies; tests will mock urlopen.
    """
    payload = build_chat_payload(system_prompt, transcription, model)
    body = json.dumps(payload).encode("utf-8")

    req = request.Request(
        GROQ_CHAT_URL,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        # try to extract an error message from the response
        try:
            err_text = exc.read().decode("utf-8")
            err_json = json.loads(err_text)
            err_msg = err_json.get("error", {}).get("message", str(exc))
        except Exception:
            err_msg = str(exc)
        raise SummaryError(f"Groq API error: {err_msg}") from exc
    except error.URLError as exc:
        raise SummaryError("Connection error to Groq API") from exc

    return parse_chat_response(resp_body)
