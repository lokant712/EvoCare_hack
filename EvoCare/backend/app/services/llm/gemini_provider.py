import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.llm.provider import LLMProvider, LLMResult
from app.services.llm.schemas import LLMStatus, ProcessingMethod
from app.services.llm.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.services.llm.clinical_reasoning_prompts import (
    CLINICAL_REASONING_SYSTEM_PROMPT,
    build_clinical_reasoning_prompt,
)
from app.services.llm.validator import ObservationValidator
from app.services.llm.safety_validator import SafetyValidator

logger = logging.getLogger(__name__)


class GeminiProvider(LLMProvider):
    """
    Google Gemini LLM Provider using the modern `google.genai` SDK.
    Optimized for Gemini 2.5 Flash / Gemini 1.5 Flash.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.model = model if model is not None else settings.GEMINI_MODEL
        self.enabled = enabled if enabled is not None else settings.LLM_ENABLED

    def is_configured(self) -> bool:
        return bool(self.enabled and self.api_key and self.api_key.strip())

    def extract_observation(self, text: str, patient_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        if not self.is_configured():
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="GEMINI_API_KEY is not configured or LLM is disabled",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            from google import genai
            from google.genai import types
        except ImportError:
            logger.warning("google.genai package is not installed in the environment")
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="google.genai package not installed",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            client = genai.Client(api_key=self.api_key)
            user_prompt = build_extraction_prompt(text, patient_context)

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.0,
                response_mime_type="application/json"
            )

            response = client.models.generate_content(
                model=self.model,
                contents=user_prompt,
                config=config
            )

            raw_response = response.text or ""
        except Exception as e:
            logger.warning(f"Gemini observation extraction API call failed: {e}")
            return LLMResult(
                status=LLMStatus.ERROR,
                error_message=f"Gemini API error: {str(e)}",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        # 1. Validate Schema
        is_valid, parsed_obs, err = ObservationValidator.validate_raw_response(raw_response, text)
        if not is_valid:
            return LLMResult(
                status=LLMStatus.VALIDATION_FAILED,
                raw_response=raw_response,
                error_message=err,
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        # 2. Validate Safety
        is_safe, violations = SafetyValidator.validate_safety(parsed_obs, text)
        if not is_safe:
            return LLMResult(
                status=LLMStatus.SAFETY_REJECTED,
                parsed_observation=parsed_obs,
                raw_response=raw_response,
                safety_violations=violations,
                error_message=f"Safety check rejected LLM output: {'; '.join(violations)}",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        return LLMResult(
            status=LLMStatus.SUCCESS,
            parsed_observation=parsed_obs,
            raw_response=raw_response,
            processing_method=ProcessingMethod.LLM_ASSISTED
        )

    def generate_clinical_reasoning(self, question: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calls Gemini Flash to generate structured clinical reasoning.
        Raises an exception on failure so the fallback cascade can transition to Groq.
        """
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured or LLM is disabled")

        from google import genai
        from google.genai import types

        client = genai.Client(api_key=self.api_key)
        user_prompt = build_clinical_reasoning_prompt(question, patient_context)

        config = types.GenerateContentConfig(
            system_instruction=CLINICAL_REASONING_SYSTEM_PROMPT,
            temperature=0.0,
            response_mime_type="application/json"
        )

        response = client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config
        )

        raw_text = response.text or "{}"
        clean_json = raw_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed = json.loads(clean_json)
        parsed["_llm_model_used"] = f"Google Gemini Flash ({self.model})"
        return parsed
