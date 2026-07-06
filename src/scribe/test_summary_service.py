"""Tests for the summary service (generate_structured_summary)."""

from unittest import TestCase, main
from unittest.mock import patch

from scribe.summary_service import generate_structured_summary, SummaryParseError


class SummaryServiceTests(TestCase):
    @patch("scribe.summary_service.summarize_transcription")
    def test_generate_structured_summary_parses_json(self, mock_summarize):
        mock_summarize.return_value = '{"title": "T1", "overview": "O", "key_points": ["a","b"], "decisions": [], "actions": ["x"]}'

        result = generate_structured_summary("sys", "trans", "APIKEY")

        self.assertEqual(result["title"], "T1")
        self.assertEqual(result["overview"], "O")
        self.assertEqual(result["key_points"], ["a","b"])  

    @patch("scribe.summary_service.summarize_transcription")
    def test_generate_structured_summary_raises_on_malformed_json(self, mock_summarize):
        mock_summarize.return_value = 'Not a JSON'

        with self.assertRaises(SummaryParseError):
            generate_structured_summary("sys", "trans", "APIKEY")


if __name__ == "__main__":
    main()
