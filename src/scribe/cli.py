from __future__ import annotations

import argparse
import datetime
import os
from pathlib import Path
from typing import Optional


def run_scribe(
    audio_path: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    out_dir: str = "outputs",
    system_prompt_path: Optional[str] = None,
    timeout: int = 30,
    *,
    transcript: Optional[str] = None,
):
    """Run the Scribe pipeline: STT -> LLM structured summary -> write Markdown.

    Returns the path to the written Markdown file as a string.
    """
    if api_key is None:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set; provide --api-key or set env var")

    # local imports to avoid import-time dependency issues during test discovery
    from scribe.summary import format_summary_markdown, load_system_prompt
    from scribe.summary_service import generate_structured_summary

    system_prompt = None
    if system_prompt_path:
        system_prompt = Path(system_prompt_path).read_text(encoding="utf-8")
    else:
        try:
            system_prompt = load_system_prompt()
        except Exception:
            system_prompt = ""

    # Transcribe (if not provided by caller)
    if transcript is None:
        # transcription module is optional in some test environments; import lazily
        from importlib import import_module

        try:
            trans_mod = import_module("scribe.transcription")
            transcript = trans_mod.transcribe_audio(audio_path, api_key=api_key, model=model)
        except Exception as exc:
            raise RuntimeError("transcription module not available") from exc

    # Summarize
    summary = generate_structured_summary(
        system_prompt, transcript, api_key=api_key, model=model, timeout=timeout
    )

    # Format and write
    markdown = format_summary_markdown(summary)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    filename = f"scribe_summary_{timestamp}.md"
    dest = out_path / filename
    dest.write_text(markdown, encoding="utf-8")

    return str(dest)


def _cli_main():
    parser = argparse.ArgumentParser(description="Run Scribe: audio -> structured summary Markdown")
    parser.add_argument("audio", help="Path to the audio file to transcribe")
    parser.add_argument("--api-key", help="Groq API key (or set GROQ_API_KEY env var)")
    parser.add_argument("--model", help="Model name to use for STT / LLM")
    parser.add_argument("--out-dir", default="outputs", help="Directory to write the Markdown output")
    parser.add_argument("--system-prompt", help="Path to a system prompt file (overrides default prompt)")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout seconds for LLM call")

    args = parser.parse_args()

    out = run_scribe(
        args.audio,
        api_key=args.api_key,
        model=args.model,
        out_dir=args.out_dir,
        system_prompt_path=args.system_prompt,
        timeout=args.timeout,
    )

    print(out)


if __name__ == "__main__":
    _cli_main()
