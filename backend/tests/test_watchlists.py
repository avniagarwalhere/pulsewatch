import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_watchlists():
    response = client.get("/api/watchlists")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "name" in data[0]

def test_create_and_delete_watchlist():
    payload = {
        "name": "Custom Test List",
        "description": "Testing CRUD",
        "color": "#10b981",
        "symbols": [
            {"symbol": "NVDA", "name": "NVIDIA", "target_price": 160.0, "tag": "Core"}
        ]
    }
    create_res = client.post("/api/watchlists", json=payload)
    assert create_res.status_code == 200
    wl = create_res.json()
    assert wl["name"] == "Custom Test List"
    assert len(wl["items"]) == 1
    assert wl["items"][0]["symbol"] == "NVDA"

    # Delete watchlist
    del_res = client.delete(f"/api/watchlists/{wl['id']}")
    assert del_res.status_code == 200
