import asyncio
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import os

# Assume the following modules are the user scripts
import era5server
import era5client

# ----------- Test setup for era5mcp -----------

def test_list_tables(monkeypatch):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [("india_df0",), ("pakistan_df0",)]
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("sqlite3.connect", lambda db: mock_conn)

    tables = era5server.list_tables()
    assert "india_df0" in tables
    assert "pakistan_df0" in tables

def test_get_sample_data_valid(monkeypatch):
    monkeypatch.setattr(era5server, "list_tables", lambda: ["india_df0"])
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        {"City": "Delhi", "date": "2020-01-01"},
        {"City": "Mumbai", "date": "2020-01-02"},
    ]
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("sqlite3.connect", lambda db: mock_conn)
    monkeypatch.setattr(mock_conn, "row_factory", lambda x: None)

    results = era5server.get_sample_data("india_df0")
    assert isinstance(results, list)
    assert results[0]["City"] == "Delhi"

def test_query_table_invalid(monkeypatch):
    monkeypatch.setattr(era5server, "list_tables", lambda: ["india_df0"])
    with pytest.raises(ValueError):
        era5server.query_table("unknown", "SELECT * FROM table_name")

def test_query_table_valid(monkeypatch):
    monkeypatch.setattr(era5server, "list_tables", lambda: ["india_df0"])
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [{"City": "Delhi", "date": "2020-01-01"}]
    mock_conn.cursor.return_value = mock_cursor
    monkeypatch.setattr("sqlite3.connect", lambda db: mock_conn)
    monkeypatch.setattr(mock_conn, "row_factory", lambda x: None)

    results = era5server.query_table("india_df0", "SELECT * FROM table_name")
    assert isinstance(results, list)
    assert results[0]["City"] == "Delhi"

# ----------- Test setup for era5optim -----------

@pytest.mark.asyncio
async def test_extract_metrics():
    question = "Compare skin temperature and total ozone in Delhi"
    metrics = await era5client.extract_metrics(question.lower())
    assert "skin_temperature" in metrics
    assert "total_ozone" in metrics

@pytest.mark.asyncio
async def test_extract_dates():
    question = "What was the wind speed in April 2022?"
    years, months = await era5client.extract_dates(question.lower())
    assert "2022" in years
    assert "04" in months

@pytest.mark.asyncio
async def test_find_tables_with_city(monkeypatch):
    session = MagicMock()
    mock_result = MagicMock()
    mock_result.content = [MagicMock(text=json.dumps({"count": 1}))]
    session.call_tool = AsyncMock(return_value=mock_result)

    tables = ["india_df0"]
    result = await era5client.find_tables_with_city(session, "Delhi", tables)
    assert "india_df0" in result

@pytest.mark.asyncio
async def test_extract_city_with_geopy(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(era5client, "find_tables_with_city", AsyncMock(return_value=["india_df0"]))
    monkeypatch.setattr(era5client, "geolocator", MagicMock())

    result = await era5client.extract_city_with_geopy("temperature in Delhi", ["temperature", "in", "Delhi"], ["skin_temperature"], ["2020"], ["01"], session, ["india_df0"])
    assert "delhi" in result or "Delhi" in result

@pytest.mark.asyncio
async def test_generate_query_no_metrics(monkeypatch):
    session = MagicMock()
    monkeypatch.setattr(era5client, "extract_metrics", AsyncMock(return_value=[]))
    result = await era5client.generate_query("What is the rainfall?", [], session)
    assert result is None

@pytest.mark.asyncio
async def test_get_climategpt_response(monkeypatch):
    monkeypatch.setenv("API_USER", "user")
    monkeypatch.setenv("API_KEY", "key")
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: MagicMock(status_code=200, json=lambda: {"choices": [{"message": {"content": "Response"}}]}))
    response = era5client.get_climategpt_response("Test question", [])
    assert response == "Response"

@pytest.mark.asyncio
async def test_process_question_response(monkeypatch):
    session = MagicMock()
    tables = ["india_df0"]
    monkeypatch.setattr(era5client, "generate_query", AsyncMock(return_value=[{
        "table_name": "india_df0",
        "query": "SELECT * FROM india_df0 WHERE City='Delhi'",
        "metric": "total_ozone",
        "city": "Delhi",
        "year": "2020",
        "month": "01"
    }]))

    mock_result = MagicMock()
    mock_result.content = [MagicMock(text=json.dumps([{"total_ozone": 280}]))]
    session.call_tool = AsyncMock(return_value=mock_result)

    monkeypatch.setattr(era5client, "get_climategpt_response", lambda q, d: "Mocked response")

    result = await era5client.process_question("What is the ozone level in Delhi?", session, tables)
    assert result["response"] == "Mocked response"
    assert result["queries"][0]["selected_table"] == "india_df0"
