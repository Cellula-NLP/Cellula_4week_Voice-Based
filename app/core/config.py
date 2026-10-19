"""Centralised, type-safe application configuration."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────
    project_name: str = "Voice Data Analyst API"
    api_v1_str: str = "/api/v1"
    data_dir: str = "./data"

    # ── LLM (Copied from your old project) ───────
    llm_model: str = "llama-3.3-70b-versatile"
    llm_fallback_model: str = "openai/gpt-oss-20b"
    llm_api_key: str = ""
    llm_base_url: str = "https://api.groq.com/openai/v1"
    llm_timeout_s: float = 60.0
    llm_temperature: float = 0.0

    # ── Speech-to-Text (Faster-Whisper) ──────────
    # 'base' or 'small' are great for CPU. 'large-v3' is best for GPU.
    whisper_model_size: str = "base"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"  # int8 is fast on CPU, float16 on GPU

    # ── Database ─────────────────────────────────
    max_upload_size_mb: int = 50

    def ensure_dirs(self) -> None:
        """Create data directories if they don't exist."""
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs()
    return s