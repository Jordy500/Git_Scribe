"""Tests for the Groq chat client (summary_client)."""

from unittest import TestCase, main
from unittest.mock import Mock, patch
from io import BytesIO

from scribe.summary_client import build_chat_payload, parse_chat_response, summarize_transcription, SummaryError


class SummaryClientTests(TestCase):
    def test_build_chat_payload_contains_system_and_user(self):
        payload = build_chat_payload("SYSTEM PROMPT", "this is a transcript", model="m")
        self.assertEqual(payload["model"], "m")
        messages = payload["messages"]
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[1]["role"], "user")

    def test_parse_chat_response_extracts_content(self):
        body = '{"choices": [{"message": {"content": "RESULT"}}]}'
        content = parse_chat_response(body)
        self.assertEqual(content, "RESULT")

    def test_parse_chat_response_raises_on_bad_json(self):
        with self.assertRaises(SummaryError):
            parse_chat_response('{}')

    @patch("scribe.summary_client.request.urlopen")
    def test_summarize_transcription_happy_path(self, mock_urlopen):
        fake_resp = Mock()
        fake_resp.read.return_value = b'{"choices": [{"message": {"content": "OK"}}]}'
        mock_urlopen.return_value.__enter__.return_value = fake_resp

        result = summarize_transcription("sys", "trans", "APIKEY", model="m")
        self.assertEqual(result, "OK")

    @patch("scribe.summary_client.request.urlopen")
    def test_summarize_transcription_handles_http_error(self, mock_urlopen):
        http_err = Mock()
        http_err.read.return_value = b'{"error": {"message": "Bad key"}}'
        from urllib import error
        mock_urlopen.side_effect = error.HTTPError(url=None, code=401, msg="", hdrs=None, fp=BytesIO(b'{"error": {"message": "Bad key"}}'))

        with self.assertRaises(SummaryError):
            summarize_transcription("sys", "trans", "APIKEY")


if __name__ == "__main__":
    main()
