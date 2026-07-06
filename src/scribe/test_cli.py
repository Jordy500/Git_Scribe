import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path


class CliPipelineTests(unittest.TestCase):
    def test_run_scribe_writes_markdown(self):
        # create a fake audio file
        with tempfile.TemporaryDirectory() as td:
            audio = Path(td) / "audio.wav"
            audio.write_text("fake-binary", encoding="utf-8")

            # import module first, then patch attributes on it to avoid import-time lookup issues
            import scribe.cli as cli_mod

            fake_summary = {
                "title": "Meeting 1",
                "overview": "Quick overview",
                "key_points": ["point1", "point2"],
                "decisions": ["decide A"],
                "actions": [{"who": "Alice", "what": "Follow up"}],
            }

            with patch(
                "scribe.summary_service.generate_structured_summary", return_value=fake_summary
            ):
                out_dir = Path(td) / "out"
                out_path = cli_mod.run_scribe(
                    str(audio), api_key="test", out_dir=str(out_dir), transcript="This is a transcript"
                )
                assert Path(out_path).exists()
                content = Path(out_path).read_text(encoding="utf-8")
                self.assertIn("Meeting 1", content)
                self.assertIn("point1", content)


if __name__ == "__main__":
    unittest.main()
