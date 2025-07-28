import sys
sys.path.append("/Users/admin/AstraTrade-Project")
from fastapi.testclient import TestClient
from apps.backend.main import app

client = TestClient(app)

def test_login_endpoint():
    response = client.post("/auth/login", 
        json={"username": "test", "password": "valid"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()