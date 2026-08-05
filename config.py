"""
Central configuration. Loads and validates environment variables once,
so agents and the orchestrator never touch os.getenv directly.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str
    gemini_model: str
    tavily_api_key: str
    output_dir: str
    llm_max_retries: int


def load_settings() -> Settings:
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()

    if not gemini_api_key:
        raise ConfigError(
            "GEMINI_API_KEY is not set. Copy .env.example to .env and add your key "
            "(get a free one at https://aistudio.google.com/apikey)."
        )
    if not tavily_api_key:
        raise ConfigError(
            "TAVILY_API_KEY is not set. Copy .env.example to .env and add your key "
            "(get a free one at https://tavily.com)."
        )

    try:
        max_retries = int(os.getenv("LLM_MAX_RETRIES", "3"))
    except ValueError as e:
        raise ConfigError("LLM_MAX_RETRIES must be an integer.") from e

    return Settings(
        gemini_api_key=gemini_api_key,
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip(),
        tavily_api_key=tavily_api_key,
        output_dir=os.getenv("OUTPUT_DIR", "output").strip(),
        llm_max_retries=max_retries,
    )
