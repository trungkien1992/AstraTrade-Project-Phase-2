import pytest
from datetime import datetime

def test_create_trade(client, test_user):
    """Test creating a new trade"""
    # First login to get token
    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]
    
    # Create trade
    response = client.post(
        "/trade",
        json={
            "asset": "EUR-USD",
            "direction": "long",
            "amount": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["outcome"] in ["profit", "loss", "breakeven"]
    assert "xp_gained" in data

def test_get_leaderboard(client):
    """Test fetching leaderboard"""
    response = client.get("/leaderboard")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data

def test_trade_invalid_symbol(client, test_user):
    """Test trade with an invalid asset symbol (should fail)."""
    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]

    response = client.post(
        "/trade",
        json={
            "asset": "INVALID-ASSET",
            "direction": "long",
            "amount": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "error" in response.json()["detail"].lower() or "fail" in response.json()["detail"].lower()

def test_trade_insufficient_funds(client, test_user):
    """Test trade with an amount likely to exceed available funds (should fail)."""
    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]

    response = client.post(
        "/trade",
        json={
            "asset": "EUR-USD",
            "direction": "long",
            "amount": 1e9  # Unrealistically large amount
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    # Accept either 400 or 422 depending on backend validation
    assert response.status_code in (400, 422)
    assert "insufficient" in response.json()["detail"].lower() or "fail" in response.json()["detail"].lower()

def test_trade_invalid_api_credentials(monkeypatch, client, test_user):
    """Test trade with invalid API credentials (should fail in production mode)."""
    # Patch settings to simulate production and invalid credentials
    from astratrade_backend.core import config
    monkeypatch.setattr(config.settings, "environment", "production")
    monkeypatch.setattr(config.settings, "exchange_api_key", "badkey")
    monkeypatch.setattr(config.settings, "exchange_secret_key", "badsecret")
    monkeypatch.setattr(config.settings, "exchange_passphrase", "badpass")

    response = client.post("/login", json={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    token = response.json()["token"]["access_token"]

    response = client.post(
        "/trade",
        json={
            "asset": "EUR-USD",
            "direction": "long",
            "amount": 10
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "exchange error" in response.json()["detail"].lower() or "fail" in response.json()["detail"].lower()
