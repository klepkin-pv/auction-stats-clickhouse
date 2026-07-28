from fastapi.testclient import TestClient


def test_health_ok(client: TestClient, mock_clickhouse):
    mock_clickhouse.command.return_value = None
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_create_bids(client: TestClient, mock_clickhouse):
    resp = client.post(
        "/api/v1/bids",
        json=[
            {"campaign_id": "cmp-1", "amount": 100.00},
            {"campaign_id": "cmp-1", "amount": 200.50},
        ],
    )
    assert resp.status_code == 200
    assert resp.json()["inserted"] == 2


def test_get_ctr_cached_and_invalidated(client: TestClient, mock_clickhouse):
    mock_clickhouse.query.return_value.result_rows = [
        ("cmp-1", 100, 5, 0.05),
    ]

    resp = client.get("/api/v1/stats/ctr?campaign_id=cmp-1")
    assert resp.status_code == 200
    assert resp.json()[0]["ctr"] == 0.05
    assert mock_clickhouse.query.call_count == 1

    resp = client.get("/api/v1/stats/ctr?campaign_id=cmp-1")
    assert resp.status_code == 200
    assert resp.json()[0]["ctr"] == 0.05
    assert mock_clickhouse.query.call_count == 1  # cached

    client.post("/api/v1/clicks", json=[{"campaign_id": "cmp-1"}])
    resp = client.get("/api/v1/stats/ctr?campaign_id=cmp-1")
    assert resp.status_code == 200
    assert mock_clickhouse.query.call_count == 2  # invalidated
