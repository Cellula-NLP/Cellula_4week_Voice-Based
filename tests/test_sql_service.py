"""Unit tests for the SQLService (Text-to-SQL)."""
import pytest
from unittest.mock import MagicMock
from app.services.sql_service import SQLService
from app.domain.models import ColumnSchema
from app.core.exceptions import LLMError, SQLError


@pytest.mark.asyncio
async def test_sql_service_successful_flow():
    # 1. Setup Mocks
    mock_llm = MagicMock()
    mock_db = MagicMock()

    # Mock DB Schema
    mock_db.get_table_schema.return_value = [
        ColumnSchema(name="category", type="TEXT"),
        ColumnSchema(name="sales", type="INTEGER")
    ]

    # Mock LLM Responses (1st call for SQL, 2nd for Explanation)
    mock_llm.complete.side_effect = [
        '{"can_answer": true, "sql": "SELECT SUM(sales) as total FROM sales_data"}',
        "The total sales are 500."
    ]

    # Mock DB Execution Result
    mock_db.execute_query.return_value = [{"total": 500}]

    # 2. Initialize Service
    service = SQLService(llm=mock_llm, db=mock_db)

    # 3. Execute
    result = await service.analyze("What are the total sales?", "sales_data")

    # 4. Assert
    assert result["generated_sql"] == "SELECT SUM(sales) as total FROM sales_data"
    assert result["result_data"] == [{"total": 500}]
    assert result["explanation"] == "The total sales are 500."

    # Ensure LLM was called exactly twice
    assert mock_llm.complete.call_count == 2
    # Ensure DB query was executed
    mock_db.execute_query.assert_called_once_with("SELECT SUM(sales) as total FROM sales_data")


@pytest.mark.asyncio
async def test_sql_service_cannot_answer():
    # Test what happens when the user asks a question irrelevant to the schema
    mock_llm = MagicMock()
    mock_db = MagicMock()

    mock_db.get_table_schema.return_value = [ColumnSchema(name="sales", type="INTEGER")]

    # LLM realizes it cannot answer
    mock_llm.complete.return_value = '{"can_answer": false, "error_reason": "The table only contains sales data, not weather data."}'

    service = SQLService(llm=mock_llm, db=mock_db)
    result = await service.analyze("What is the weather today?", "sales_data")

    assert result["generated_sql"] == ""
    assert result["result_data"] == []
    assert "The table only contains sales data" in result["explanation"]

    # Ensure DB was NEVER called because LLM said "cannot answer"
    mock_db.execute_query.assert_not_called()


@pytest.mark.asyncio
async def test_sql_service_database_error():
    mock_llm = MagicMock()
    mock_db = MagicMock()

    mock_db.get_table_schema.return_value = [ColumnSchema(name="sales", type="INTEGER")]
    mock_llm.complete.return_value = '{"can_answer": true, "sql": "SELECT * FROM sales_data"}'

    # Simulate SQLite raising an error (e.g., syntax error)
    mock_db.execute_query.side_effect = SQLError("Invalid SQL syntax")

    service = SQLService(llm=mock_llm, db=mock_db)

    with pytest.raises(SQLError):
        await service.analyze("Show me data", "sales_data")