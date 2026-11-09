import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# Add backend directory to Python import path
BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.hindsight_service import HindsightMemoryService


@pytest.fixture
def mock_service(monkeypatch):
    monkeypatch.setenv("HINDSIGHT_API_KEY", "test-api-key")

    with patch("app.services.hindsight_service.Hindsight") as mock_hindsight:
        mock_client = MagicMock()
        mock_hindsight.return_value = mock_client

        service = HindsightMemoryService()

        yield service, mock_client

        service.close()


def test_verified_incident_is_stored(mock_service):
    service, client = mock_service

    result = service.store_verified_incident(
        incident_id="TEST-001",
        logs="Database connection timeout",
        root_cause="Database connection pool exhausted",
        resolution="Increased connection pool size",
        service_name="payment-service",
        severity="high",
        verified=True
    )

    assert result["success"] is True
    assert result["incident_id"] == "TEST-001"
    client.retain.assert_called_once()

    call_args = client.retain.call_args.kwargs
    assert call_args["metadata"]["verified"] == "true"
    assert call_args["metadata"]["incident_id"] == "TEST-001"


def test_unverified_incident_is_rejected(mock_service):
    service, client = mock_service

    with pytest.raises(
        ValueError,
        match="Only verified incidents can be stored"
    ):
        service.store_verified_incident(
            incident_id="TEST-002",
            logs="Database timeout",
            root_cause="Unknown",
            resolution="Unknown",
            service_name="payment-service",
            verified=False
        )

    client.retain.assert_not_called()


def test_missing_incident_information_is_rejected(mock_service):
    service, client = mock_service

    with pytest.raises(
        ValueError,
        match="Required incident information is missing"
    ):
        service.store_verified_incident(
            incident_id="TEST-003",
            logs="Database timeout",
            root_cause="Database failure",
            resolution="",
            service_name="payment-service",
            verified=True
        )

    client.retain.assert_not_called()


def test_similar_incidents_are_recalled(mock_service):
    service, client = mock_service

    client.recall.return_value = SimpleNamespace(
        results=[
            SimpleNamespace(
                type="experience",
                text="Previous database timeout resolved by increasing pool size"
            ),
            SimpleNamespace(
                type="world",
                text="Database connection pool configuration"
            )
        ]
    )

    result = service.recall_similar_incidents(
        logs="Database connection timeout",
        service_name="payment-service"
    )

    assert result["success"] is True
    assert result["count"] == 2
    assert len(result["incidents"]) == 2

    assert result["incidents"][0]["type"] == "experience"
    assert "increasing pool size" in result["incidents"][0]["content"]

    client.recall.assert_called_once()


def test_empty_logs_are_rejected(mock_service):
    service, client = mock_service

    with pytest.raises(
        ValueError,
        match="Incident logs cannot be empty"
    ):
        service.recall_similar_incidents(
            logs="   ",
            service_name="payment-service"
        )

    client.recall.assert_not_called()


def test_hindsight_recall_error_is_propagated(mock_service):
    service, client = mock_service

    client.recall.side_effect = RuntimeError("Hindsight service unavailable")

    with pytest.raises(
        RuntimeError,
        match="Hindsight service unavailable"
    ):
        service.recall_similar_incidents(
            logs="Database connection timeout",
            service_name="payment-service"
        )


def test_missing_api_key_is_rejected(monkeypatch):
    monkeypatch.delenv("HINDSIGHT_API_KEY", raising=False)

    with patch("app.services.hindsight_service.Hindsight") as mock_hindsight:
        with pytest.raises(
            ValueError,
            match="HINDSIGHT_API_KEY is not configured"
        ):
            HindsightMemoryService()

        mock_hindsight.assert_not_called()


def test_hindsight_connection_is_closed(mock_service):
    service, client = mock_service

    service.close()

    client.close.assert_called_once()
