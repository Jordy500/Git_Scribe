import os
import tempfile
import unittest

from scribe.config import load_config


class ConfigTests(unittest.TestCase):
    def test_load_config_from_env(self):
        os.environ["GROQ_API_KEY"] = "abc123"
        os.environ["SCRIBE_STT_MODEL"] = "stt-x"
        os.environ["SCRIBE_LLM_MODEL"] = "llm-y"
        cfg = load_config()
        self.assertEqual(cfg.groq_api_key, "abc123")
        self.assertEqual(cfg.stt_model, "stt-x")
        self.assertEqual(cfg.llm_model, "llm-y")


if __name__ == "__main__":
    unittest.main()
