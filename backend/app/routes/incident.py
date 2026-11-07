import logging
from functools import lru_cache
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.incident import (
    IncidentAnalyzeRequest,
    IncidentAnalysisResponse,
    IncidentVerifyRequest,
    IncidentVerifyResponse,
    IncidentDetailResponse,
)
from app.services.incident_service import IncidentService, IncidentNotFoundError
from app.services.groq_service import GroqServiceError
from app.services.hindsight_service import HindsightServiceError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/incidents", tags=["Incidents"])


@lru_cache()
def get_incident_service() -> IncidentService:
    """Dependency provider for the incident management service."""
    return IncidentService()


@router.post(
    "/analyze",
    response_model=IncidentAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze incident logs",
    description="Submits application/server logs to retrieve historical context from Hindsight and AI analysis from Groq."
)
def analyze_incident(
    payload: IncidentAnalyzeRequest,
    service: IncidentService = Depends(get_incident_service)
) -> IncidentAnalysisResponse:
    try:
        return service.analyze_incident(
            logs=payload.logs,
            service=payload.service
        )
    except GroqServiceError as e:
        logger.error("Incident analysis failed due to Groq service error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"AI analysis service error: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.exception("Unexpected error during incident analysis: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the incident analysis."
        )


@router.post(
    "/{incident_id}/verify",
    response_model=IncidentVerifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify an incident and store in memory",
    description="Allows an engineer to confirm the actual root cause and resolution, retaining it in Hindsight long-term memory."
)
def verify_incident(
    incident_id: str,
    payload: IncidentVerifyRequest,
    service: IncidentService = Depends(get_incident_service)
) -> IncidentVerifyResponse:
    try:
        return service.verify_incident(
            incident_id=incident_id,
            actual_root_cause=payload.actual_root_cause,
            resolution=payload.resolution,
            verified=payload.verified
        )
    except IncidentNotFoundError as e:
        logger.warning("Attempted to verify non-existent incident %s", incident_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HindsightServiceError as e:
        logger.error("Hindsight retention failed for incident %s: %s", incident_id, e)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Hindsight memory storage failed: {str(e)}"
        )
    except Exception as e:
        logger.exception("Unexpected error during incident verification: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while storing the verified incident."
        )


@router.get(
    "/{incident_id}",
    response_model=IncidentDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get incident details",
    description="Returns the details, analysis findings, and verification status of a specific incident."
)
def get_incident(
    incident_id: str,
    service: IncidentService = Depends(get_incident_service)
) -> IncidentDetailResponse:
    try:
        return service.get_incident(incident_id=incident_id)
    except IncidentNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
