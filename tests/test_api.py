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


def test_stats_filters_reach_clickhouse(client: TestClient, mock_clickhouse):
    resp = client.get(
        "/api/v1/stats/revenue",
        params={
            "campaign_id": "cmp-1",
            "date_from": "2026-01-01T00:00:00Z",
            "date_to": "2026-01-02T00:00:00+03:00",
            "limit": 10,
            "offset": 5,
        },
    )
    assert resp.status_code == 200

    sql = mock_clickhouse.query.call_args.args[0]
    params = mock_clickhouse.query.call_args.kwargs["parameters"]
    assert "created_at >= toDateTime(%(date_from)s)" in sql
    assert "created_at <= toDateTime(%(date_to)s)" in sql
    assert "LIMIT 10 OFFSET 5" in sql
    assert params == {
        "campaign_id": "cmp-1",
        "date_from": "2026-01-01 00:00:00",
        "date_to": "2026-01-01 21:00:00",
    }


def test_ctr_date_filter_targets_impressions(client: TestClient, mock_clickhouse):
    resp = client.get(
        "/api/v1/stats/ctr",
        params={"campaign_id": "cmp-1", "date_from": "2026-01-01"},
    )
    assert resp.status_code == 200

    sql = mock_clickhouse.query.call_args.args[0]
    assert (
        "WHERE i.campaign_id = %(campaign_id)s"
        " AND i.created_at >= toDateTime(%(date_from)s)" in sql
    )


def test_stats_cache_key_includes_filters(client: TestClient, mock_clickhouse):
    client.get("/api/v1/stats/cpm", params={"limit": 10})
    client.get("/api/v1/stats/cpm", params={"limit": 10})
    assert mock_clickhouse.query.call_count == 1  # cached

    client.get("/api/v1/stats/cpm", params={"limit": 20})
    assert mock_clickhouse.query.call_count == 2  # другой limit — другой ключ

    client.get("/api/v1/stats/cpm", params={"limit": 10, "offset": 10})
    assert mock_clickhouse.query.call_count == 3


def test_invalid_date_range_returns_400(client: TestClient, mock_clickhouse):
    resp = client.get(
        "/api/v1/stats/ctr",
        params={"date_from": "2026-02-01", "date_to": "2026-01-01"},
    )
    assert resp.status_code == 400
    assert mock_clickhouse.query.call_count == 0


def test_pagination_bounds_are_validated(client: TestClient, mock_clickhouse):
    assert client.get("/api/v1/stats/ctr", params={"limit": 0}).status_code == 422
    assert client.get("/api/v1/stats/ctr", params={"limit": 501}).status_code == 422
    assert client.get("/api/v1/stats/ctr", params={"offset": -1}).status_code == 422
