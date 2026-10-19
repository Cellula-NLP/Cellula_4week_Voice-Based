"""Domain-specific exception hierarchy."""
from __future__ import annotations


class AppError(Exception):
    """Base application error."""


class STTError(AppError):
    """Speech-to-text transcription failed."""


class LLMError(AppError):
    """LLM provider returned an error."""


class SQLError(AppError):
    """SQL Generation or Execution failed."""


class DatasetError(AppError):
    """Dataset processing failed."""