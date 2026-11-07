from datetime import datetime, timezone
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class PossibleCause(BaseModel):
    """Possible root cause suggested by AI analysis."""
    cause: str = Field(..., description="Suggested possible root cause")
    confidence: str = Field(..., description="Confidence level: high, medium, or low")
    reason: str = Field(..., description="Reasoning based on the log evidence")


class HistoricalMatch(BaseModel):
    """Historical verified incident retrieved from Hindsight memory."""
    incident_id: Optional[str] = Field(None, description="Identifier of the historical incident")
    service: Optional[str] = Field(None, description="Service affected in the historical incident")
    root_cause: str = Field(..., description="Engineer-verified root cause from history")
    resolution: str = Field(..., description="Confirmed resolution from history")
    similarity_context: Optional[str] = Field(None, description="Context or matching symptoms")


# ==========================================
# API Request / Response Schemas
# ==========================================

class IncidentAnalyzeRequest(BaseModel):
    """Request payload to analyze server or application logs."""
    logs: str = Field(..., description="Raw server or application log text")
    service: str = Field("unknown-service", description="Name of the affected service or component")

    @field_validator("logs")
    @classmethod
    def validate_logs(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Logs content cannot be empty or only whitespace")
        if len(trimmed) > 50000:
            raise ValueError("Logs content exceeds maximum allowed size of 50,000 characters")
        return trimmed

    @field_validator("service")
    @classmethod
    def validate_service(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            return "unknown-service"
        return trimmed


class IncidentAnalysisResponse(BaseModel):
    """Response payload containing AI analysis and recalled historical memory."""
    incident_id: str = Field(..., description="Unique tracking ID for the incident")
    service: str = Field(..., description="Affected service name")
    severity: str = Field(..., description="Assessed incident severity: CRITICAL, HIGH, MEDIUM, or LOW")
    possible_causes: List[PossibleCause] = Field(
        default_factory=list,
        description="Suggested possible root causes (not confirmed facts)"
    )
    evidence: List[str] = Field(
        default_factory=list,
        description="Key diagnostic evidence extracted from logs"
    )
    recommended_checks: List[str] = Field(
        default_factory=list,
        description="Recommended safe diagnostic steps for engineers"
    )
    historical_matches: List[HistoricalMatch] = Field(
        default_factory=list,
        description="Similar verified incidents retrieved from Hindsight memory"
    )
    verified: bool = Field(False, description="Verification status (always False initially)")
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Timestamp of the analysis"
    )


class IncidentVerifyRequest(BaseModel):
    """Request payload to verify an incident and retain in Hindsight memory."""
    actual_root_cause: str = Field(..., description="The engineer-confirmed root cause")
    resolution: str = Field(..., description="The verified resolution applied to resolve the incident")
    verified: bool = Field(..., description="Explicit confirmation of verification (must be true)")

    @field_validator("actual_root_cause")
    @classmethod
    def validate_actual_root_cause(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Actual root cause cannot be empty")
        return trimmed

    @field_validator("resolution")
    @classmethod
    def validate_resolution(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed:
            raise ValueError("Resolution cannot be empty")
        return trimmed

    @field_validator("verified")
    @classmethod
    def validate_verified(cls, v: bool) -> bool:
        if not v:
            raise ValueError("The 'verified' flag must be true to verify and store this incident")
        return v


class IncidentVerifyResponse(BaseModel):
    """Response payload after an incident is verified."""
    success: bool = Field(..., description="Whether the verification succeeded")
    incident_id: str = Field(..., description="Verified incident ID")
    message: str = Field(..., description="Status message")
    stored_in_memory: bool = Field(..., description="Whether retained in Hindsight long-term memory")
    verified_at: str = Field(..., description="Timestamp of verification")


class IncidentDetailResponse(BaseModel):
    """Detailed view of an incident including analysis and verification status."""
    incident_id: str
    service: str
    severity: str
    logs: str
    possible_causes: List[PossibleCause]
    evidence: List[str]
    recommended_checks: List[str]
    historical_matches: List[HistoricalMatch]
    verified: bool
    actual_root_cause: Optional[str] = None
    resolution: Optional[str] = None
    created_at: str
    verified_at: Optional[str] = None
