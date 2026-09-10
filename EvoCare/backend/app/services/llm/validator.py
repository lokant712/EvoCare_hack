import json
import logging
from typing import Dict, Any, Tuple, Optional
from pydantic import ValidationError
from app.services.llm.schemas import ParsedCaregiverObservation, LLMStatus

logger = logging.getLogger(__name__)

class ObservationValidator:
    @staticmethod
    def validate_raw_response(raw_response: str, raw_statement: str) -> Tuple[bool, Optional[ParsedCaregiverObservation], Optional[str]]:
        """
        Validates raw string/JSON output from LLM against Pydantic schema ParsedCaregiverObservation.
        Returns (is_valid, parsed_observation, error_message).
        """
        if not raw_response or not raw_response.strip():
            return False, None, "Empty response received from LLM"

        cleaned = raw_response.strip()
        # Strip markdown code fences if model returned ```json ... ```
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Malformed JSON from LLM: {e}")
            return False, None, f"Malformed JSON: {str(e)}"

        if not isinstance(data, dict):
            return False, None, "LLM response must be a JSON object"

        # Ensure raw_statement is preserved
        if not data.get("raw_statement"):
            data["raw_statement"] = raw_statement

        try:
            obs = ParsedCaregiverObservation(**data)
            return True, obs, None
        except ValidationError as e:
            logger.warning(f"Schema validation error on LLM response: {e}")
            return False, None, f"Schema validation error: {str(e)}"
        except Exception as e:
            logger.warning(f"Unexpected validation error: {e}")
            return False, None, f"Unexpected validation error: {str(e)}"
