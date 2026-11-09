import sys
from pathlib import Path
import json
import logging
from typing import List, Optional, Any

from pydantic import BaseModel, Field, ValidationError

# Ensure backend root is in sys.path
_backend_dir = str(Path(__file__).resolve().parent.parent.parent)
if _backend_dir not in sys.path:
    sys.path.insert(0, _backend_dir)

from groq import Groq, APIError, APITimeoutError, RateLimitError

try:
    from app.config import get_settings
    from app.schemas.incident import PossibleCause
except ImportError:
    from backend.app.config import get_settings
    from backend.app.schemas.incident import PossibleCause

logger = logging.getLogger(__name__)


class GroqServiceError(Exception):
    """Custom exception raised when Groq analysis fails."""
    pass


class GroqAnalysisResult(BaseModel):
    """Structured analysis returned by the Groq LLM."""

    severity: str = Field(
        "MEDIUM",
        description="Severity level: CRITICAL, HIGH, MEDIUM, or LOW"
    )

    possible_causes: List[PossibleCause] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommended_checks: List[str] = Field(default_factory=list)


class GroqService:
    """Service to communicate with Groq API for incident log analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ):
        settings = get_settings()

        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self._client: Optional[Groq] = None

    @property
    def client(self) -> Groq:
        """Lazily initialize Groq client."""

        if not self.api_key:
            raise GroqServiceError(
                "GROQ_API_KEY is not configured in environment variables."
            )

        if self._client is None:
            self._client = Groq(api_key=self.api_key)

        return self._client

    def is_configured(self) -> bool:
        return bool(
            self.api_key and not self.api_key.startswith("your_")
        )

    @staticmethod
    def _normalize_causes(raw_causes: Any) -> List[dict]:
        """
        Normalize Groq possible_causes into a consistent list
        of dictionaries matching the PossibleCause schema.
        """

        if raw_causes is None:
            return []

        if isinstance(raw_causes, str):
            raw_causes = [raw_causes]

        if not isinstance(raw_causes, list):
            raise GroqServiceError(
                "Groq returned possible_causes in an invalid format."
            )

        normalized = []

        for index, item in enumerate(raw_causes):

            if isinstance(item, str):
                cause = item.strip()

                if not cause:
                    continue

                normalized.append({
                    "cause": cause,
                    "confidence": "medium",
                    "reason": "Suggested by Groq based on the supplied logs."
                })

            elif isinstance(item, dict):
                cause = item.get("cause") or item.get("title")

                if not isinstance(cause, str) or not cause.strip():
                    logger.warning(
                        "Skipping cause item %s because cause is missing.",
                        index
                    )
                    continue

                confidence = str(
                    item.get("confidence", "medium")
                ).lower()

                if confidence not in {"high", "medium", "low"}:
                    confidence = "medium"

                reason = item.get("reason", "")

                if not isinstance(reason, str) or not reason.strip():
                    reason = (
                        "Suggested based on the available incident logs."
                    )

                normalized.append({
                    "cause": cause.strip(),
                    "confidence": confidence,
                    "reason": reason.strip()
                })

            else:
                logger.warning(
                    "Skipping unsupported possible cause item at index %s.",
                    index
                )

        return normalized

    def analyze_logs(
        self,
        logs: str,
        service: str = "unknown-service",
        historical_context: Optional[str] = None
    ) -> GroqAnalysisResult:

        system_prompt = (
            "You are an expert site reliability engineer and incident "
            "response assistant.\n"
            "Analyze application/server logs and historical verified incidents.\n"
            "Suggest possible root causes, evidence, severity and safe "
            "diagnostic checks.\n\n"
            "Safety rules:\n"
            "1. Possible causes are suggestions, never confirmed facts.\n"
            "2. Never claim an unverified cause is confirmed.\n"
            "3. Never execute automated repairs.\n"
            "4. Base evidence on supplied logs.\n\n"
            "Return ONLY a valid JSON object:\n"
            "{\n"
            '  "severity": "CRITICAL",\n'
            '  "possible_causes": [\n'
            '    {\n'
            '      "cause": "Possible cause",\n'
            '      "confidence": "high",\n'
            '      "reason": "Explanation based on logs"\n'
            '    }\n'
            '  ],\n'
            '  "evidence": ["Log evidence"],\n'
            '  "recommended_checks": ["Safe diagnostic check"]\n'
            "}\n"
            "Every possible_causes item MUST be a JSON object, "
            "never a plain string."
        )

        history_section = (
            f"\n\nHISTORICAL VERIFIED INCIDENTS:\n{historical_context}\n"
            if historical_context and historical_context.strip()
            else "\n\nNo relevant historical incidents found."
        )

        user_prompt = (
            f"Service Name: {service}\n\n"
            f"Current Incident Logs:\n{logs}"
            f"{history_section}\n"
            "Return the investigation analysis as JSON."
        )

        try:
            logger.info(
                "Submitting incident logs to Groq model: %s",
                self.model
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
                max_tokens=2048
            )

            raw_content = response.choices[0].message.content

            if not raw_content:
                raise GroqServiceError(
                    "Groq model returned an empty response."
                )

            parsed_json = json.loads(raw_content)

            if not isinstance(parsed_json, dict):
                raise GroqServiceError(
                    "Groq returned JSON, but the root value was not an object."
                )

            severity = str(
                parsed_json.get("severity", "MEDIUM")
            ).upper()

            if severity not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                severity = "MEDIUM"

            parsed_json["severity"] = severity

            parsed_json["possible_causes"] = (
                self._normalize_causes(
                    parsed_json.get("possible_causes", [])
                )
            )

            for field in ["evidence", "recommended_checks"]:
                value = parsed_json.get(field, [])

                if isinstance(value, str):
                    value = [value]

                if not isinstance(value, list):
                    value = []

                parsed_json[field] = [
                    str(item).strip()
                    for item in value
                    if item is not None and str(item).strip()
                ]

            return GroqAnalysisResult.model_validate(parsed_json)

        except RateLimitError as e:
            logger.error("Groq rate limit exceeded: %s", e)
            raise GroqServiceError(
                "Groq API rate limit exceeded. Please retry shortly."
            ) from e

        except APITimeoutError as e:
            logger.error("Groq request timed out: %s", e)
            raise GroqServiceError(
                "Groq API request timed out."
            ) from e

        except APIError as e:
            logger.error("Groq API error: %s", e)
            raise GroqServiceError(
                "Groq API request failed."
            ) from e

        except json.JSONDecodeError as e:
            logger.error("Invalid JSON from Groq: %s", e)
            raise GroqServiceError(
                "Groq returned invalid JSON formatting."
            ) from e

        except ValidationError as e:
            logger.error(
                "Groq response failed schema validation: %s",
                e
            )
            raise GroqServiceError(
                "Groq response did not match the required analysis schema."
            ) from e

        except Exception as e:
            if isinstance(e, GroqServiceError):
                raise

            logger.exception(
                "Unexpected error during Groq analysis."
            )

            raise GroqServiceError(
                "Failed to analyze incident with Groq."
            ) from e