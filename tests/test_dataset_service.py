"""Unit tests for the DatasetService."""
import pytest
from unittest.mock import MagicMock
from app.services.dataset_service import DatasetService
from app.domain.models import ColumnSchema
from app.core.exceptions import DatasetError


def test_dataset_upload_success():
    mock_db = MagicMock()
    mock_db.create_table_from_csv.return_value = (
        100,
        [ColumnSchema(name="id", type="INTEGER"), ColumnSchema(name="name", type="TEXT")]
    )

    service = DatasetService(db=mock_db)
    table_name, row_count, schema = service.process_upload("fake/path.csv", "employees.csv")

    assert table_name == "employees"
    assert row_count == 100
    assert len(schema) == 2
    assert schema[1].name == "name"


def test_dataset_upload_invalid_extension():
    mock_db = MagicMock()
    service = DatasetService(db=mock_db)

    with pytest.raises(DatasetError, match="Only CSV files are supported."):
        service.process_upload("fake/path.xlsx", "data.xlsx")