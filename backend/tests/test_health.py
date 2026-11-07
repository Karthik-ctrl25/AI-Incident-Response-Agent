import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200_and_expected_payload():
    """Verify health endpoint returns HTTP 200 with expected status message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "message": "Incident Response Backend is running"
    }

