import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from app.schemas.incident import (
    IncidentAnalysisResponse,
    IncidentVerifyResponse,
    IncidentDetailResponse,
    HistoricalMatch,
    PossibleCause,
)
from app.services.groq_service import GroqService, GroqServiceError
from app.services.hindsight_service import (
    HindsightMemoryService,
    HindsightServiceError,
)

logger = logging.getLogger(__name__)


class IncidentNotFoundError(Exception):
    """Raised when an incident ID does not exist in the active store."""
    pass


class IncidentService:
    """
    Core incident management service coordinating Groq analysis,
    Hindsight memory recall, verification, and active incident state.
    """

    def __init__(
        self,
        groq_service: Optional[GroqService] = None,
        hindsight_service: Optional[HindsightMemoryService] = None
    ):
        self.groq_service = groq_service or GroqService()
        self.hindsight_service = hindsight_service or HindsightMemoryService()
        # In-memory store for active hackathon sessions
        # NOTE: In-memory data is reset if the server restarts.
        self._store: Dict[str, Dict[str, Any]] = {}

    def _parse_historical_memories(self, memories: List[Dict[str, Any]]) -> tuple[str, List[HistoricalMatch]]:
        """Parse raw memories from Hindsight into prompt text and HistoricalMatch objects."""
        if not memories:
            return "", []

        prompt_lines: List[str] = []
        historical_matches: List[HistoricalMatch] = []

        for idx, mem in enumerate(memories, start=1):
            content = mem.get("content", "")
            prompt_lines.append(f"Incident Memory #{idx}:\n{content.strip()}\n")

            # Extract fields if formatted using the standard incident template
            inc_id_match = re.search(r"Incident ID:\s*([^\n\r]+)", content)
            service_match = re.search(r"Service:\s*([^\n\r]+)", content)
            root_cause_match = re.search(r"Verified Root Cause:\s*([\s\S]*?)(?=Successful Resolution:|$)", content)
            resolution_match = re.search(r"Successful Resolution:\s*([\s\S]*?)(?=Verification Status:|$)", content)

            root_cause = root_cause_match.group(1).strip() if root_cause_match else "Historical verified cause"
            resolution = resolution_match.group(1).strip() if resolution_match else "Historical verified resolution"

            historical_matches.append(
                HistoricalMatch(
                    incident_id=inc_id_match.group(1).strip() if inc_id_match else f"HIST-{idx}",
                    service=service_match.group(1).strip() if service_match else None,
                    root_cause=root_cause,
                    resolution=resolution,
                    similarity_context=content[:250].strip()
                )
            )

        historical_prompt = "\n".join(prompt_lines)
        return historical_prompt, historical_matches

    def analyze_incident(self, logs: str, service: str) -> IncidentAnalysisResponse:
        """
        Analyze incident logs:
        1. Recalls similar historical verified incidents from Hindsight memory.
        2. Passes logs and historical context to Groq for analysis.
        3. Returns structured findings and registers active incident.
        """
        incident_id = f"INC-{uuid.uuid4().hex[:8].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()

        # Step 1: Query Hindsight memory
        historical_context = ""
        historical_matches: List[HistoricalMatch] = []
        try:
            recall_result = self.hindsight_service.recall_similar_incidents(
                logs=logs,
                service_name=service
            )
            raw_memories = recall_result.get("incidents", [])
            historical_context, historical_matches = self._parse_historical_memories(raw_memories)
            logger.info("Retrieved %d historical matches from Hindsight", len(historical_matches))
        except HindsightServiceError as e:
            logger.warning("Hindsight recall failed; proceeding with fresh analysis without memory: %s", e)
        except Exception as e:
            logger.warning("Unexpected error during Hindsight recall; continuing: %s", e)

        # Step 2: Query Groq LLM
        groq_result = self.groq_service.analyze_logs(
            logs=logs,
            service=service,
            historical_context=historical_context
        )

        response = IncidentAnalysisResponse(
            incident_id=incident_id,
            service=service,
            severity=groq_result.severity,
            possible_causes=groq_result.possible_causes,
            evidence=groq_result.evidence,
            recommended_checks=groq_result.recommended_checks,
            historical_matches=historical_matches,
            verified=False,
            created_at=created_at
        )

        # Step 3: Register in active incident store
        self._store[incident_id] = {
            "incident_id": incident_id,
            "service": service,
            "severity": groq_result.severity,
            "logs": logs,
            "possible_causes": [c.model_dump() for c in groq_result.possible_causes],
            "evidence": groq_result.evidence,
            "recommended_checks": groq_result.recommended_checks,
            "historical_matches": [m.model_dump() for m in historical_matches],
            "verified": False,
            "actual_root_cause": None,
            "resolution": None,
            "created_at": created_at,
            "verified_at": None,
        }

        return response

    def verify_incident(
        self,
        incident_id: str,
        actual_root_cause: str,
        resolution: str,
        verified: bool = True
    ) -> IncidentVerifyResponse:
        """
        Confirm an incident with engineer-verified root cause and resolution.
        Stores the verified incident into Hindsight long-term memory.
        """
        if not verified:
            raise ValueError("The 'verified' flag must be true to verify this incident.")

        if incident_id not in self._store:
            raise IncidentNotFoundError(f"Incident with ID '{incident_id}' not found in active session store.")

        record = self._store[incident_id]

        # Retain confirmed incident in Hindsight Cloud
        logger.info("Storing verified incident %s into Hindsight memory", incident_id)
        self.hindsight_service.store_verified_incident(
            incident_id=incident_id,
            logs=record["logs"],
            root_cause=actual_root_cause,
            resolution=resolution,
            service_name=record["service"],
            severity=record["severity"],
            verified=True
        )

        verified_at = datetime.now(timezone.utc).isoformat()
        record["verified"] = True
        record["actual_root_cause"] = actual_root_cause
        record["resolution"] = resolution
        record["verified_at"] = verified_at

        return IncidentVerifyResponse(
            success=True,
            incident_id=incident_id,
            message="Incident verified and retained in Hindsight memory successfully.",
            stored_in_memory=True,
            verified_at=verified_at
        )

    def get_incident(self, incident_id: str) -> IncidentDetailResponse:
        """Retrieve details of an incident from the active store."""
        if incident_id not in self._store:
            raise IncidentNotFoundError(f"Incident with ID '{incident_id}' not found.")

        data = self._store[incident_id]
        return IncidentDetailResponse(
            incident_id=data["incident_id"],
            service=data["service"],
            severity=data["severity"],
            logs=data["logs"],
            possible_causes=[PossibleCause(**c) for c in data["possible_causes"]],
            evidence=data["evidence"],
            recommended_checks=data["recommended_checks"],
            historical_matches=[HistoricalMatch(**m) for m in data["historical_matches"]],
            verified=data["verified"],
            actual_root_cause=data.get("actual_root_cause"),
            resolution=data.get("resolution"),
            created_at=data["created_at"],
            verified_at=data.get("verified_at"),
        )

    def clear(self):
        """Clear the in-memory incident store (useful for test isolation)."""
        self._store.clear()
