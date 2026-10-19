# app/infrastructure/database/sqlite_manager.py
"""SQLite implementation of the DatabaseManager."""
from __future__ import annotations

import logging
import os
import sqlite3
from typing import Any

import pandas as pd
import sqlglot
from sqlglot import exp

from app.core.config import get_settings
from app.core.exceptions import DatasetError, SQLError
from app.domain.models import ColumnSchema
from app.domain.ports import DatabaseManager

logger = logging.getLogger(__name__)


class SQLiteManager(DatabaseManager):
    """Manages SQLite database operations for uploaded datasets."""

    def __init__(self) -> None:
        self._settings = get_settings()
        # We will use a single SQLite file for all uploaded tables
        self._db_path = os.path.join(self._settings.data_dir, "analytics.db")
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        """Create a new connection to the SQLite database."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row  # Allows fetching rows as dictionaries
        return conn

    def _init_db(self) -> None:
        """Ensure the database file exists."""
        with self._get_conn() as conn:
            pass  # The connection itself creates the file if it doesn't exist

    def create_table_from_csv(self, csv_path: str, table_name: str) -> tuple[int, list[ColumnSchema]]:
        """Reads a CSV, writes it to SQLite, and returns the schema."""
        if not os.path.exists(csv_path):
            raise DatasetError(f"File not found: {csv_path}")

        try:
            # 1. Read CSV into Pandas
            df = pd.read_csv(csv_path)

            if df.empty:
                raise DatasetError("The uploaded CSV file is empty.")

            # Sanitize table name to prevent SQL injection via table names
            safe_table_name = "".join(c for c in table_name if c.isalnum() or c == "_").lower()
            if not safe_table_name:
                safe_table_name = "uploaded_data"

            # 2. Write to SQLite
            with self._get_conn() as conn:
                # If a table with this name exists, drop it (overwrite)
                conn.execute(f"DROP TABLE IF EXISTS {safe_table_name}")

                # Write the dataframe to SQLite
                df.to_sql(safe_table_name, conn, index=False, if_exists="replace")

            logger.info("Successfully created table '%s' with %d rows.", safe_table_name, len(df))

            # 3. Get the schema
            schema = self.get_table_schema(safe_table_name)

            return len(df), schema

        except pd.errors.EmptyDataError:
            raise DatasetError("The CSV file is empty or malformed.")
        except Exception as exc:
            logger.error("Failed to process CSV: %s", exc)
            raise DatasetError(f"Failed to process dataset: {exc}") from exc

    def get_table_schema(self, table_name: str) -> list[ColumnSchema]:
        """Fetch column names and data types from the SQLite database."""
        schema: list[ColumnSchema] = []
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                # PRAGMA table_info returns: (cid, name, type, notnull, dflt_value, pk)
                cursor.execute(f"PRAGMA table_info({table_name})")
                rows = cursor.fetchall()

                for row in rows:
                    schema.append(ColumnSchema(
                        name=row["name"],
                        type=row["type"]
                    ))
            return schema
        except Exception as exc:
            logger.error("Failed to fetch schema for %s: %s", table_name, exc)
            raise DatasetError(f"Could not read table schema: {exc}") from exc

    def execute_query(self, query: str) -> list[dict[str, Any]]:
        """
        Execute a SELECT query safely.
        Uses sqlglot to ensure the query is a read-only SELECT statement.
        """
        # ── SECURITY: Validate the query using sqlglot ──
        try:
            parsed = sqlglot.parse(query, read="sqlite")
            if not parsed:
                raise SQLError("Empty SQL query.")

            for statement in parsed:
                # Must be a SELECT statement
                if not isinstance(statement, exp.Select):
                    raise SQLError("Security Violation: Only SELECT queries are allowed.")

                # Ensure there's no sneaky DROP/DELETE hidden inside
                if statement.find(exp.Drop) or statement.find(exp.Delete) or statement.find(exp.Update):
                    raise SQLError("Security Violation: Destructive commands detected.")

        except sqlglot.errors.ParseError as exc:
            raise SQLError(f"Invalid SQL syntax: {exc}") from exc

        # ── EXECUTE ──
        try:
            with self._get_conn() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                rows = cursor.fetchall()

                # Convert sqlite3.Row objects to standard dictionaries for JSON
                return [dict(row) for row in rows]

        except sqlite3.Error as exc:
            logger.error("SQLite execution error: %s", exc)
            raise SQLError(f"Database execution failed: {exc}") from exc