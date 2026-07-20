def test_create_bid(client):
    response = client.post(
        "/bids",
        json={
            "lot_id": "lot-1",
            "bidder_id": "user-1",
            "amount": "100.50",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["lot_id"] == "lot-1"
    assert data["bidder_id"] == "user-1"
    assert data["amount"] == "100.50"


def test_stats_not_found(client):
    response = client.get("/stats/non-existent-lot")
    assert response.status_code == 404


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["database"] == "connected"
