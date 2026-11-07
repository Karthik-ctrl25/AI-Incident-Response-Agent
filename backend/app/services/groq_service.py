import json
import logging
from typing import List, Optional
from pydantic import BaseModel, Field

from groq import Groq, APIError, APITimeoutError, RateLimitError
from app.config import get_settings
from app.schemas.incident import PossibleCause

logger = logging.getLogger(__name__)


class GroqServiceError(Exception):
    """Custom exception raised when Groq analysis fails."""
    pass


class GroqAnalysisResult(BaseModel):
    """Structured analysis returned by the Groq LLM."""
    severity: str = Field("MEDIUM", description="Severity level: CRITICAL, HIGH, MEDIUM, or LOW")
    possible_causes: List[PossibleCause] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)
    recommended_checks: List[str] = Field(default_factory=list)


class GroqService:
    """Service to communicate with the Groq API for incident log analysis."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROQ_API_KEY
        self.model = model or settings.GROQ_MODEL
        self._client: Optional[Groq] = None

    @property
    def client(self) -> Groq:
        """Lazily initialize the Groq client."""
        if not self.api_key:
            raise GroqServiceError("GROQ_API_KEY is not configured in environment variables.")
        if self._client is None:
            self._client = Groq(api_key=self.api_key)
        return self._client

    def is_configured(self) -> bool:
        """Check if Groq API credentials are provided."""
        return bool(self.api_key and not self.api_key.startswith("your_"))

    def analyze_logs(
        self,
        logs: str,
        service: str = "unknown-service",
        historical_context: Optional[str] = None
    ) -> GroqAnalysisResult:
        """
        Analyze raw incident logs with optional historical memory context.
        Returns a structured GroqAnalysisResult validated with Pydantic.
        """
        system_prompt = (
            "You are an expert site reliability engineer and incident response assistant.\n"
            "Analyze the provided application/server logs and any supplied historical verified incidents.\n"
            "Your goal is to suggest possible root causes, extract key log evidence, assess severity, "
            "and suggest safe diagnostic checks for engineers.\n\n"
            "MANDATORY SAFETY RULES:\n"
            "1. Possible root causes and recommended checks are suggestions for investigation, NEVER confirmed facts.\n"
            "2. Never claim that a possible cause is verified.\n"
            "3. Never suggest or execute automated server repairs or unsafe write operations.\n"
            "4. Base your evidence strictly on verbatim snippets or factual points from the logs.\n\n"
            "You must return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "severity": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",\n'
            '  "possible_causes": [\n'
            '    {"cause": "Summary of possible cause", "confidence": "high"|"medium"|"low", "reason": "Explanation"}\n'
            "  ],\n"
            '  "evidence": ["Log snippet 1", "Log snippet 2"],\n'
            '  "recommended_checks": ["Investigation check 1", "Investigation check 2"]\n'
            "}"
        )

        history_section = (
            f"\n\nHISTORICAL VERIFIED INCIDENTS (From Hindsight Long-Term Memory):\n{historical_context}\n"
            "NOTE: Use this historical knowledge to guide your suspected causes and checks if the symptoms match."
            if historical_context and historical_context.strip()
            else "\n\nHISTORICAL CONTEXT: No relevant previous verified incidents were found in memory."
        )

        user_prompt = (
            f"Service Name: {service}\n\n"
            f"Current Incident Logs:\n{logs}"
            f"{history_section}\n\n"
            "Provide your investigation analysis in the requested JSON format."
        )

        try:
            logger.info("Submitting incident logs to Groq model: %s", self.model)
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
                raise GroqServiceError("Groq model returned an empty response.")

            parsed_json = json.loads(raw_content)

            # Ensure severity is uppercase and valid
            severity = str(parsed_json.get("severity", "MEDIUM")).upper()
            if severity not in {"CRITICAL", "HIGH", "MEDIUM", "LOW"}:
                severity = "HIGH" if "error" in logs.lower() or "fail" in logs.lower() else "MEDIUM"
            parsed_json["severity"] = severity

            # Validate against Pydantic model
            return GroqAnalysisResult.model_validate(parsed_json)

        except RateLimitError as e:
            logger.error("Groq rate limit exceeded: %s", e)
            raise GroqServiceError("Groq API rate limit exceeded. Please retry shortly.") from e
        except APITimeoutError as e:
            logger.error("Groq request timed out: %s", e)
            raise GroqServiceError("Groq API request timed out.") from e
        except APIError as e:
            logger.error("Groq API error: %s", e)
            raise GroqServiceError(f"Groq API error: {e.message}") from e
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from Groq response: %s", e)
            raise GroqServiceError("Groq returned invalid JSON formatting.") from e
        except Exception as e:
            if isinstance(e, GroqServiceError):
                raise
            logger.exception("Unexpected error during Groq analysis: %s", e)
            raise GroqServiceError(f"Failed to analyze incident with Groq: {str(e)}") from e
