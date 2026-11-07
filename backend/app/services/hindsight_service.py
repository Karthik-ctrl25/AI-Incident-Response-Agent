import os
import json
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from hindsight_client import Hindsight
from app.config import get_settings

load_dotenv()

logger = logging.getLogger(__name__)


class HindsightServiceError(Exception):
    """Custom exception raised when Hindsight operations fail."""
    pass


class HindsightMemoryService:
    """Service to interact with Hindsight Cloud for incident memory retention and recall."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        bank_id: Optional[str] = None
    ):
        settings = get_settings()
        self.api_key = api_key or os.getenv("HINDSIGHT_API_KEY") or settings.HINDSIGHT_API_KEY
        self.base_url = (
            base_url
            or os.getenv("HINDSIGHT_BASE_URL")
            or settings.HINDSIGHT_BASE_URL
            or "https://api.hindsight.vectorize.io"
        )
        self.bank_id = (
            bank_id
            or os.getenv("HINDSIGHT_BANK_ID")
            or settings.HINDSIGHT_BANK_ID
            or "incident-response-memory"
        )
        self._client: Optional[Hindsight] = None

    @property
    def client(self) -> Hindsight:
        """Lazily initialize the Hindsight client."""
        if not self.is_configured():
            raise HindsightServiceError("HINDSIGHT_API_KEY is not configured")
        if self._client is None:
            self._client = Hindsight(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=30.0
            )
        return self._client

    def is_configured(self) -> bool:
        """Check whether valid Hindsight credentials are configured."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    # -----------------------------------------
    # 1. STORE VERIFIED INCIDENT
    # -----------------------------------------

    def store_verified_incident(
        self,
        incident_id: str,
        logs: str,
        root_cause: str,
        resolution: str,
        service_name: str,
        severity: str = "unknown",
        verified: bool = False
    ) -> Dict[str, Any]:
        """Store an engineer-verified incident in Hindsight long-term memory."""
        if not verified:
            raise ValueError("Only verified incidents can be stored")

        if not all([
            incident_id,
            logs,
            root_cause,
            resolution,
            service_name
        ]):
            raise ValueError("Required incident information is missing")

        content = f"""
VERIFIED HISTORICAL INCIDENT

Incident ID: {incident_id}

Service: {service_name}

Severity: {severity}

Original Logs:
{logs}

Verified Root Cause:
{root_cause}

Successful Resolution:
{resolution}

Verification Status: Verified
"""

        try:
            result = self.client.retain(
                bank_id=self.bank_id,
                content=content,
                context=(
                    "Engineer-verified production incident "
                    "and its confirmed resolution."
                ),
                metadata={
                    "incident_id": str(incident_id),
                    "service_name": str(service_name),
                    "severity": str(severity),
                    "verified": "true"
                }
            )

            logger.info("Incident stored successfully in Hindsight: %s", incident_id)

            return {
                "success": True,
                "incident_id": incident_id,
                "message": "Incident stored successfully"
            }

        except Exception as e:
            logger.exception("Failed to store incident in Hindsight: %s", incident_id)
            if isinstance(e, ValueError):
                raise
            raise HindsightServiceError(f"Hindsight storage failed: {str(e)}") from e

    # -----------------------------------------
    # 2. RECALL SIMILAR HISTORICAL INCIDENTS
    # -----------------------------------------

    def recall_similar_incidents(
        self,
        logs: str,
        service_name: Optional[str] = None,
        max_tokens: int = 4096,
        budget: str = "mid"
    ) -> Dict[str, Any]:
        """Recall historical verified incidents similar to current logs."""
        if not logs or not logs.strip():
            raise ValueError("Incident logs cannot be empty")

        if not self.is_configured():
            logger.warning("Hindsight is not configured; skipping memory recall.")
            return {
                "success": False,
                "count": 0,
                "incidents": [],
                "message": "HINDSIGHT_API_KEY is not configured"
            }

        query = f"""
Find historical incidents relevant to the following current server/application incident.

Service:
{service_name or "Unknown"}

Current Incident Logs:
{logs}

Prioritize incidents with similar:
- Error messages
- Exception types
- Stack traces
- Failed components
- Database or network failures
- Root causes
- Successful resolutions

Return only genuinely relevant historical incidents.
"""

        try:
            result = self.client.recall(
                bank_id=self.bank_id,
                query=query,
                max_tokens=max_tokens,
                budget=budget
            )

            incidents: List[Dict[str, Any]] = []

            for memory in getattr(result, "results", []):
                incidents.append({
                    "type": getattr(memory, "type", "memory"),
                    "content": getattr(memory, "text", str(memory))
                })

            logger.info("Retrieved %d historical memories from Hindsight", len(incidents))

            return {
                "success": True,
                "count": len(incidents),
                "incidents": incidents
            }

        except Exception as e:
            logger.exception("Hindsight recall failed")
            raise HindsightServiceError(f"Hindsight recall failed: {str(e)}") from e

    # -----------------------------------------
    # 3. CLOSE CONNECTION
    # -----------------------------------------

    def close(self):
        """Close active Hindsight client session."""
        if self._client:
            try:
                self._client.close()
                logger.info("Hindsight connection closed")
            except Exception as e:
                logger.warning("Error closing Hindsight client: %s", e)
            finally:
                self._client = None


if __name__ == "__main__":
    service = HindsightMemoryService()
    try:
        result = service.recall_similar_incidents(
            logs="Database connection timeout",
            service_name="payment-service"
        )
        print(json.dumps(result, indent=4))
    finally:
        service.close()
