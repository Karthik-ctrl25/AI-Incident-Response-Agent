import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

try:
    from app.main import app
except ImportError:
    from backend.app.main import app

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
