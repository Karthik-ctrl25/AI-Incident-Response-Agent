import sys
from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Ensure backend root is in sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

try:
    from app.main import app
    from app.routes.incident import get_incident_service
    from app.services.incident_service import IncidentService
    from app.services.groq_service import GroqService, GroqServiceError, GroqAnalysisResult
    from app.services.hindsight_service import HindsightMemoryService, HindsightServiceError
    from app.schemas.incident import PossibleCause
except ImportError:
    from backend.app.main import app
    from backend.app.routes.incident import get_incident_service
    from backend.app.services.incident_service import IncidentService
    from backend.app.services.groq_service import GroqService, GroqServiceError, GroqAnalysisResult
    from backend.app.services.hindsight_service import HindsightMemoryService, HindsightServiceError
    from backend.app.schemas.incident import PossibleCause


@pytest.fixture
def mock_groq_service():
    """Fixture providing a mocked Groq service."""
    service = MagicMock(spec=GroqService)
    service.is_configured.return_value = True
    service.analyze_logs.return_value = GroqAnalysisResult(
        severity="HIGH",
        possible_causes=[
            PossibleCause(
                cause="Database connection pool exhausted",
                confidence="high",
                reason="Logs show timeout acquiring connections while pool is 95% full."
            )
        ],
        evidence=[
            "Connection pool usage reached 95%",
            "Connection timeout after 15000ms"
        ],
        recommended_checks=[
            "Inspect database connection pool size",
            "Review database active queries"
        ]
    )
    return service


@pytest.fixture
def mock_hindsight_service():
    """Fixture providing a mocked Hindsight memory service."""
    service = MagicMock(spec=HindsightMemoryService)
    service.is_configured.return_value = True
    service.recall_similar_incidents.return_value = {
        "success": True,
        "count": 0,
        "incidents": []
    }
    service.store_verified_incident.return_value = {
        "success": True,
        "incident_id": "INC-TEST",
        "message": "Incident stored successfully"
    }
    return service


@pytest.fixture
def test_client(mock_groq_service, mock_hindsight_service):
    """TestClient wired with mocked incident services."""
    incident_service = IncidentService(
        groq_service=mock_groq_service,
        hindsight_service=mock_hindsight_service
    )
    app.dependency_overrides[get_incident_service] = lambda: incident_service
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ============================================================
# 1. Health Endpoint Test
# ============================================================
def test_health_endpoint(test_client):
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Incident Response Backend is running"
    }


# ============================================================
# 2. Empty Log Submission Test
# ============================================================
def test_empty_log_submission(test_client):
    response = test_client.post(
        "/api/incidents/analyze",
        json={"logs": "   ", "service": "payment-service"}
    )
    assert response.status_code == 422


# ============================================================
# 3. Valid Incident Analysis Request Test
# ============================================================
def test_valid_incident_analysis_request(test_client):
    response = test_client.post(
        "/api/incidents/analyze",
        json={
            "logs": "ERROR: Database connection timed out after 15000ms",
            "service": "payment-service"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["incident_id"].startswith("INC-")
    assert data["service"] == "payment-service"
    assert data["severity"] == "HIGH"
    assert len(data["possible_causes"]) == 1
    assert data["possible_causes"][0]["cause"] == "Database connection pool exhausted"
    assert data["possible_causes"][0]["confidence"] == "high"
    assert len(data["evidence"]) >= 1
    assert len(data["recommended_checks"]) >= 1
    assert data["verified"] is False


# ============================================================
# 4. Invalid Input Tests
# ============================================================
def test_invalid_input_missing_logs(test_client):
    response = test_client.post(
        "/api/incidents/analyze",
        json={"service": "payment-service"}
    )
    assert response.status_code == 422


def test_invalid_input_excessively_large_logs(test_client):
    oversized_logs = "A" * 50001
    response = test_client.post(
        "/api/incidents/analyze",
        json={"logs": oversized_logs, "service": "payment-service"}
    )
    assert response.status_code == 422


# ============================================================
# 5. Groq API Failure Test
# ============================================================
def test_groq_api_failure(test_client, mock_groq_service):
    mock_groq_service.analyze_logs.side_effect = GroqServiceError("Groq API rate limit exceeded")
    response = test_client.post(
        "/api/incidents/analyze",
        json={
            "logs": "ERROR: Database connection failed",
            "service": "order-service"
        }
    )
    assert response.status_code == 502
    assert "AI analysis service error" in response.json()["detail"]


# ============================================================
# 6. Hindsight Retrieval Failure Test (Graceful Degradation)
# ============================================================
def test_hindsight_retrieval_failure_degrades_gracefully(test_client, mock_hindsight_service):
    mock_hindsight_service.recall_similar_incidents.side_effect = HindsightServiceError("Hindsight cloud unavailable")
    response = test_client.post(
        "/api/incidents/analyze",
        json={
            "logs": "ERROR: Timeout waiting for PostgreSQL",
            "service": "auth-service"
        }
    )
    # The analysis should still succeed without crashing
    assert response.status_code == 200
    data = response.json()
    assert data["historical_matches"] == []
    assert data["severity"] == "HIGH"


# ============================================================
# 7. Verification With verified=False Test
# ============================================================
def test_verification_with_verified_false(test_client):
    # First analyze
    analysis_resp = test_client.post(
        "/api/incidents/analyze",
        json={"logs": "ERROR: Crash", "service": "billing"}
    )
    inc_id = analysis_resp.json()["incident_id"]

    # Attempt to verify with verified=False
    verify_resp = test_client.post(
        f"/api/incidents/{inc_id}/verify",
        json={
            "actual_root_cause": "Deadlock",
            "resolution": "Restarted workers",
            "verified": False
        }
    )
    assert verify_resp.status_code == 422


# ============================================================
# 8. Successful Verification Test
# ============================================================
def test_successful_verification(test_client, mock_hindsight_service):
    # Analyze first
    analysis_resp = test_client.post(
        "/api/incidents/analyze",
        json={"logs": "ERROR: Pool exhausted", "service": "payment-service"}
    )
    inc_id = analysis_resp.json()["incident_id"]

    # Verify
    verify_resp = test_client.post(
        f"/api/incidents/{inc_id}/verify",
        json={
            "actual_root_cause": "Max connections reached on PostgreSQL",
            "resolution": "Increased max_connections to 200 and enabled connection pooling",
            "verified": True
        }
    )
    assert verify_resp.status_code == 200
    vdata = verify_resp.json()
    assert vdata["success"] is True
    assert vdata["stored_in_memory"] is True
    assert vdata["incident_id"] == inc_id

    # Verify that Hindsight store was invoked with verified=True
    mock_hindsight_service.store_verified_incident.assert_called_once()
    call_kwargs = mock_hindsight_service.store_verified_incident.call_args.kwargs
    assert call_kwargs["verified"] is True
    assert call_kwargs["root_cause"] == "Max connections reached on PostgreSQL"

    # Check incident details endpoint reflects verified status
    get_resp = test_client.get(f"/api/incidents/{inc_id}")
    assert get_resp.status_code == 200
    detail = get_resp.json()
    assert detail["verified"] is True
    assert detail["actual_root_cause"] == "Max connections reached on PostgreSQL"


# ============================================================
# 9. Hindsight Storage Failure Test
# ============================================================
def test_hindsight_storage_failure(test_client, mock_hindsight_service):
    # Analyze
    analysis_resp = test_client.post(
        "/api/incidents/analyze",
        json={"logs": "ERROR: Network partition", "service": "gateway"}
    )
    inc_id = analysis_resp.json()["incident_id"]

    # Mock storage failure
    mock_hindsight_service.store_verified_incident.side_effect = HindsightServiceError("Write failure to Hindsight")

    verify_resp = test_client.post(
        f"/api/incidents/{inc_id}/verify",
        json={
            "actual_root_cause": "Switch misconfiguration",
            "resolution": "Updated VLAN routes",
            "verified": True
        }
    )
    assert verify_resp.status_code == 502
    assert "Hindsight memory storage failed" in verify_resp.json()["detail"]

    # Details should NOT show verified as True
    get_resp = test_client.get(f"/api/incidents/{inc_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["verified"] is False


# ============================================================
# 10. Repeated Similar Incident Retrieval Test
# ============================================================
def test_repeated_similar_incident_retrieval(test_client, mock_hindsight_service, mock_groq_service):
    # Simulate historical memory found in Hindsight
    mock_hindsight_service.recall_similar_incidents.return_value = {
        "success": True,
        "count": 1,
        "incidents": [
            {
                "type": "memory",
                "content": (
                    "VERIFIED HISTORICAL INCIDENT\n"
                    "Incident ID: INC-001\n"
                    "Service: payment-service\n"
                    "Severity: HIGH\n"
                    "Original Logs:\nDatabase connection timeout\n"
                    "Verified Root Cause:\nPostgreSQL connection pool exhausted\n"
                    "Successful Resolution:\nIncreased pool capacity to 50 connections\n"
                    "Verification Status: Verified"
                )
            }
        ]
    }

    response = test_client.post(
        "/api/incidents/analyze",
        json={
            "logs": "OperationalError: could not connect to server: Connection timed out",
            "service": "payment-service"
        }
    )
    assert response.status_code == 200
    data = response.json()

    # Historical match should be present
    assert len(data["historical_matches"]) == 1
    match = data["historical_matches"][0]
    assert match["incident_id"] == "INC-001"
    assert match["root_cause"] == "PostgreSQL connection pool exhausted"
    assert match["resolution"] == "Increased pool capacity to 50 connections"

    # Groq service should have received historical context in its call
    mock_groq_service.analyze_logs.assert_called_once()
    groq_call_kwargs = mock_groq_service.analyze_logs.call_args.kwargs
    assert "PostgreSQL connection pool exhausted" in groq_call_kwargs["historical_context"]
