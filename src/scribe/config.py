from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

try:
    # optional dependency for reading .env files in local dev
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - if python-dotenv not installed, fallback to env
    load_dotenv = None


@dataclass
class Config:
    groq_api_key: Optional[str]
    stt_model: Optional[str]
    llm_model: Optional[str]


def load_config(env_path: Optional[str] = None) -> Config:
    """Load configuration from environment or an optional .env file.

    - If `env_path` is provided and python-dotenv is installed, it will be loaded.
    - Primary source of truth are environment variables (so CI/production can set them securely).
    """
    if env_path and load_dotenv:
        load_dotenv(env_path)

    groq_api_key = os.environ.get("GROQ_API_KEY")
    stt_model = os.environ.get("SCRIBE_STT_MODEL") or os.environ.get("STT_MODEL")
    llm_model = os.environ.get("SCRIBE_LLM_MODEL") or os.environ.get("LLM_MODEL")

    return Config(groq_api_key=groq_api_key, stt_model=stt_model, llm_model=llm_model)


def get_config() -> Config:
    """Convenience accessor that loads the configuration from the environment.

    Use `load_config(env_path)` in local dev if you want to load from a `.env` file.
    """
    return load_config()
