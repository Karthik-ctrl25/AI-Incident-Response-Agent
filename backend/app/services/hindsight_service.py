import os
import json
import logging

from datetime import datetime, timezone
from typing import Optional

from dotenv import load_dotenv
from hindsight_client import Hindsight


load_dotenv()

logger = logging.getLogger(__name__)


class HindsightMemoryService:

    def __init__(self):

        self.api_key = os.getenv("HINDSIGHT_API_KEY")

        self.base_url = os.getenv(
            "HINDSIGHT_BASE_URL",
            "https://api.hindsight.vectorize.io"
        )

        self.bank_id = os.getenv(
            "HINDSIGHT_BANK_ID",
            "incident-response-memory"
        )

        if not self.api_key:
            raise ValueError(
                "HINDSIGHT_API_KEY is not configured"
            )

        self.client = Hindsight(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=30.0
        )

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
    ):

        if not verified:
            raise ValueError(
                "Only verified incidents can be stored"
            )

        if not all([
            incident_id,
            logs,
            root_cause,
            resolution,
            service_name
        ]):
            raise ValueError(
                "Required incident information is missing"
            )

        incident = {
            "incident_id": incident_id,
            "service_name": service_name,
            "severity": severity,
            "logs": logs,
            "root_cause": root_cause,
            "resolution": resolution,
            "verified": True,
            "verified_at": datetime.now(
                timezone.utc
            ).isoformat()
        }

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

            logger.info(
                "Incident stored successfully: %s",
                incident_id
            )

            return {
                "success": True,
                "incident_id": incident_id,
                "message": "Incident stored successfully"
            }

        except Exception:

            logger.exception(
                "Failed to store incident: %s",
                incident_id
            )

            raise

    # -----------------------------------------
    # 2. RECALL SIMILAR HISTORICAL INCIDENTS
    # -----------------------------------------

    def recall_similar_incidents(
        self,
        logs: str,
        service_name: Optional[str] = None,
        max_tokens: int = 4096,
        budget: str = "mid"
    ):

        if not logs or not logs.strip():
            raise ValueError(
                "Incident logs cannot be empty"
            )

        query = f"""
        Find historical incidents relevant to the
        following current server/application incident.

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

            incidents = []

            for memory in result.results:

                incidents.append({
                    "type": memory.type,
                    "content": memory.text
                })

            logger.info(
                "Retrieved %d historical memories",
                len(incidents)
            )

            return {
                "success": True,
                "count": len(incidents),
                "incidents": incidents
            }

        except Exception:

            logger.exception(
                "Hindsight recall failed"
            )

            raise

    # -----------------------------------------
    # 3. CLOSE CONNECTION
    # -----------------------------------------

    def close(self):

        if self.client:
            self.client.close()
            logger.info(
                "Hindsight connection closed"
            )


# ---------------------------------------------
# OPTIONAL: QUICK CONNECTION TEST
# ---------------------------------------------

if __name__ == "__main__":

    service = HindsightMemoryService()

    try:

        result = service.recall_similar_incidents(
            logs="Database connection timeout",
            service_name="payment-service"
        )

        print(json.dumps(
            result,
            indent=4
        ))

    finally:
        service.close()