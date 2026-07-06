"""Service layer to produce a structured summary from a transcription.

This small layer calls the LLM client and expects the assistant to return a
JSON object with the following shape:
{
  "title": "...",
  "overview": "...",
  "key_points": ["..."],
  "decisions": ["..."],
  "actions": ["..."]
}

We keep this layer minimal so it can be explained in an oral review.
"""

import json
from typing import Dict, Any

from .summary_client import summarize_transcription, SummaryError


class SummaryParseError(Exception):
    pass


def generate_structured_summary(system_prompt: str, transcription: str, api_key: str, model: str = None, timeout: int = 30) -> Dict[str, Any]:
    """Call the LLM and parse a structured JSON summary.

    The function expects the assistant to return valid JSON. If parsing fails,
    we raise `SummaryParseError` to make explicit that the LLM output was
    malformed.
    """
    model_arg = model if model is not None else None
    try:
        assistant_text = summarize_transcription(system_prompt, transcription, api_key, model=model_arg, timeout=timeout)
    except SummaryError as exc:
        raise

    # Try parsing assistant text as JSON
    try:
        data = json.loads(assistant_text)
    except Exception as exc:
        raise SummaryParseError(f"Failed to parse assistant output as JSON: {exc}\nOutput: {assistant_text}") from exc

    # Ensure expected keys exist and normalize types
    result = {
        "title": str(data.get("title", "")),
        "overview": str(data.get("overview", "")),
        "key_points": list(data.get("key_points", [])),
        "decisions": list(data.get("decisions", [])),
        "actions": list(data.get("actions", [])),
    }

    return result
