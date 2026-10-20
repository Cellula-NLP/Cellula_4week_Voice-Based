"""Abstract Ports (Interfaces) for Dependency Inversion."""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence
from app.domain.models import ColumnSchema


class SpeechToTextProvider(ABC):
    """Port for Audio Transcription."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> tuple[str, str]:
        """
        Transcribe audio file to text.
        Returns: (transcript_text, detected_language_code)
        """
        ...


class DatabaseManager(ABC):
    """Port for SQLite Database operations."""

    @abstractmethod
    def create_table_from_csv(self, csv_path: str, table_name: str) -> tuple[str, int, list[ColumnSchema]]:
        """
        Reads a CSV, creates a SQLite table, and returns (sanitized_table_name, row_count, schema).
        """
        ...

    @abstractmethod
    def get_table_schema(self, table_name: str) -> list[ColumnSchema]:
        """Fetch the columns and types for a specific table."""
        ...

    @abstractmethod
    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a SELECT query and return the results as a list of dictionaries.
        Must raise an exception if the query is dangerous (e.g., DROP TABLE).
        """
        ...


class LLMProvider(ABC):
    """Port for LLM interaction."""

    @abstractmethod
    async def complete(
        self,
        messages: Sequence[dict],
        *,
        json_mode: bool = False,
        temperature: float | None = None,
    ) -> str:
        """Return a complete text response from the LLM."""
        ...