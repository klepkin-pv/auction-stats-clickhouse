import pytest
from fastapi.testclient import TestClient

from app.db.clickhouse import get_client
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        ch = get_client()
        ch.execute("TRUNCATE TABLE IF EXISTS bids_raw")
        ch.execute("TRUNCATE TABLE IF EXISTS bids_stats")
        yield test_client
        ch.execute("TRUNCATE TABLE IF EXISTS bids_raw")
        ch.execute("TRUNCATE TABLE IF EXISTS bids_stats")
