"""Helpers for building and formatting Scribe summaries."""

from pathlib import Path
from typing import Dict, Iterable, List


PROJECT_ROOT = Path(__file__).resolve().parents[2]
SUMMARY_PROMPT_PATH = PROJECT_ROOT / "prompts" / "summary_system_prompt.txt"


def load_system_prompt() -> str:
    """Load the summary system prompt from disk."""
    return SUMMARY_PROMPT_PATH.read_text(encoding="utf-8").strip()


def format_summary_markdown(summary: Dict[str, object]) -> str:
    """Format a summary dictionary as Markdown."""
    title = str(summary.get("title", "Compte rendu"))
    overview = str(summary.get("overview", ""))
    key_points = list(summary.get("key_points", []))
    decisions = list(summary.get("decisions", []))
    actions = list(summary.get("actions", []))

    lines: List[str] = [f"# {title}", ""]
    if overview:
        lines.extend(["## Résumé", overview, ""])
    if key_points:
        lines.extend(["## Points clés"])
        lines.extend(f"- {point}" for point in key_points)
        lines.append("")
    if decisions:
        lines.extend(["## Décisions"])
        lines.extend(f"- {decision}" for decision in decisions)
        lines.append("")
    if actions:
        lines.extend(["## Actions"])
        lines.extend(f"- {action}" for action in actions)
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
