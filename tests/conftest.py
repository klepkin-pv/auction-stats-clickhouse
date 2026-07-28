from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from src.cache import _memory_cache
from src.main import app


@pytest.fixture
def client():
    _memory_cache.clear()
    return TestClient(app)


@pytest.fixture
def mock_clickhouse():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []
    mock_client.command.return_value = None
    with patch("src.clickhouse.client.get_client", return_value=mock_client):
        with patch("src.api.router.get_client", return_value=mock_client):
            with patch("src.main.get_client", return_value=mock_client):
                yield mock_client
