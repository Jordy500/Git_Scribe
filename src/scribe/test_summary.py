"""Tests for the summary helpers."""

from pathlib import Path
from unittest import TestCase, main

from scribe.summary import SUMMARY_PROMPT_PATH, format_summary_markdown, load_system_prompt


class SummaryPromptTests(TestCase):
    def test_load_system_prompt_reads_text_file(self):
        prompt = load_system_prompt()

        self.assertIn("assistant de synthèse", prompt)
        self.assertTrue(SUMMARY_PROMPT_PATH.exists())


class SummaryFormattingTests(TestCase):
    def test_format_summary_markdown_builds_sections(self):
        markdown = format_summary_markdown(
            {
                "title": "Réunion produit",
                "overview": "Le groupe a validé le lancement.",
                "key_points": ["Point A", "Point B"],
                "decisions": ["On lance en juillet."],
                "actions": ["Alice prépare la démo."],
            }
        )

        self.assertIn("# Réunion produit", markdown)
        self.assertIn("## Résumé", markdown)
        self.assertIn("## Points clés", markdown)
        self.assertIn("## Décisions", markdown)
        self.assertIn("## Actions", markdown)
        self.assertTrue(markdown.endswith("\n"))


if __name__ == "__main__":
    main()
