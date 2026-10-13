"""Integration tests for Trading Journal API endpoints."""

import os
import sys
from pathlib import Path
from datetime import datetime, UTC
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

SRC_PATH = Path(__file__).parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from app import app

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_BASE = f"{BASE_URL}/api"


@pytest.fixture(scope="module")
def client():
    """Create a reusable in-process API client."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="module")
def created_trade_id(client):
    """Create one trade for tests that need a concrete trade id."""
    unique_suffix = uuid4().hex[:10]
    now_iso = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
    trade_data = {
        "direction": "buy",
        "code": "AAPL",
        "quantity": 1.0,
        "orderNumber": {
            "name": f"POS_TEST_{unique_suffix}",
            "link": "positionHistory/test",
            "id": f"trade-{unique_suffix}",
            "frontend": "SYSTEM",
            "positionId": f"{unique_suffix}",
        },
        "price": 150.5,
        "closePrice": 151.25,
        "resultGross": 0.75,
        "realisedProfitLossAccountCurrency": 0.75,
        "resultNet": 0.75,
        "eventNumber": {
            "name": f"PO_TEST_{unique_suffix}",
            "id": f"event-{unique_suffix}",
        },
        "eventType": "closed",
        "time": now_iso,
        "openingTime": now_iso,
        "fxFee": 0.0,
        "resultAfterFxFeeAccountCurrency": 0.75,
        "instrumentCurrency": "USD",
        "accountCurrency": "EUR",
        "netResultAccountCurrency": 0.75,
        "realisedProfitLossInstrumentCurrency": 0.8,
    }
    response = client.post("/api/trades/", json=trade_data)
    assert response.status_code == 201, f"Unexpected create trade status={response.status_code}, body={response.text}"
    data = response.json()
    assert data.get("id") is not None
    return data["id"]


@pytest.fixture(scope="module")
def created_journal_id(client):
    """Create one journal entry for tests that need a concrete entry id."""
    unique_suffix = uuid4().hex[:10]
    entry_data = {
        "title": f"Test Entry {unique_suffix}",
        "content": "This is a test journal entry created through the REST API.",
        "tags": "test,api,demo",
    }
    response = client.post("/api/journal/", json=entry_data)
    assert response.status_code == 201, f"Unexpected create journal status={response.status_code}, body={response.text}"
    data = response.json()
    assert data.get("id") is not None
    return data["id"]


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "healthy"


def test_create_trade(created_trade_id):
    """Trade fixture created an id."""
    assert isinstance(created_trade_id, int)


def test_get_trades(client):
    """Test getting recent trades."""
    params = {"limit": 5, "include_overnight": True}
    response = client.get("/api/trades/", params=params)
    assert response.status_code == 200
    trades = response.json()
    assert isinstance(trades, list)


def test_get_trade_by_id(client, created_trade_id):
    """Test getting a specific trade."""
    response = client.get(f"/api/trades/{created_trade_id}")
    assert response.status_code == 200
    trade = response.json()
    assert trade.get("id") == created_trade_id


def test_create_journal_entry(created_journal_id):
    """Journal fixture created an id."""
    assert isinstance(created_journal_id, int)


def test_get_journal_entries(client):
    """Test getting journal entries."""
    params = {"limit": 5}
    response = client.get("/api/journal/", params=params)
    assert response.status_code == 200
    entries = response.json()
    assert isinstance(entries, list)


def test_get_analytics(client):
    """Test getting analytics."""
    response = client.get("/api/analytics/")
    assert response.status_code == 200
    data = response.json()
    for key in ["total_trades", "winning_trades", "losing_trades", "net_profit"]:
        assert key in data
