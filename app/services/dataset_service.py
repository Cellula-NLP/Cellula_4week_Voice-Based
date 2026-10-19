# app/services/dataset_service.py
from __future__ import annotations
import logging
from app.domain.models import ColumnSchema
from app.domain.ports import DatabaseManager
from app.core.exceptions import DatasetError

logger = logging.getLogger(__name__)


class DatasetService:
    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def process_upload(self, csv_path: str, filename: str) -> tuple[str, int, list[ColumnSchema]]:
        """Processes the uploaded CSV and returns (table_name, row_count, schema)."""
        if not filename.endswith(".csv"):
            raise DatasetError("Only CSV files are supported.")

        try:
            import os
            table_name = os.path.splitext(filename)[0].lower()

            # The DB manager handles the Pandas -> SQLite logic
            row_count, schema = self._db.create_table_from_csv(csv_path, table_name)

            if row_count == 0:
                raise DatasetError("The uploaded CSV is empty.")

            return table_name, row_count, schema
        except Exception as exc:
            logger.error("Dataset processing failed: %s", exc)
            raise DatasetError(str(exc)) from exc