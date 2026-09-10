import json
import logging
from typing import Dict, Any, Optional
from app.core.config import settings
from app.services.llm.provider import LLMProvider, LLMResult, MockLLMProvider
from app.services.llm.schemas import LLMStatus, ProcessingMethod
from app.services.llm.prompts import SYSTEM_PROMPT, build_extraction_prompt
from app.services.llm.clinical_reasoning_prompts import (
    CLINICAL_REASONING_SYSTEM_PROMPT,
    build_clinical_reasoning_prompt,
)
from app.services.llm.validator import ObservationValidator
from app.services.llm.safety_validator import SafetyValidator

logger = logging.getLogger(__name__)


class AnthropicProvider(LLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        reasoning_model: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.api_key = api_key if api_key is not None else settings.ANTHROPIC_API_KEY
        self.model = model if model is not None else settings.ANTHROPIC_MODEL
        self.reasoning_model = reasoning_model if reasoning_model is not None else settings.CLINICAL_REASONING_MODEL
        self.enabled = enabled if enabled is not None else settings.LLM_ENABLED

    def extract_observation(self, text: str, patient_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        if not self.enabled:
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="LLM extraction is disabled via configuration",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        if not self.api_key or not self.api_key.strip():
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="ANTHROPIC_API_KEY is not configured",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            import anthropic
        except ImportError:
            logger.warning("Anthropic package is not installed in the current environment")
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="Anthropic library not installed",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            client = anthropic.Anthropic(api_key=self.api_key)
            user_prompt = build_extraction_prompt(text, patient_context)

            message = client.messages.create(
                model=self.model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.0
            )

            raw_response = message.content[0].text if message.content else ""
        except Exception as e:
            logger.warning(f"Anthropic API call failed: {e}")
            return LLMResult(
                status=LLMStatus.ERROR,
                error_message=f"Anthropic API error: {str(e)}",
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
        Calls Claude 3.5 Sonnet to generate structured clinical reasoning.
        Falls back seamlessly to deterministic mock reasoning if API key is not configured.
        """
        if not self.enabled or not self.api_key or not self.api_key.strip():
            logger.info("Using deterministic Mock LLM provider for clinical reasoning (No API key).")
            return MockLLMProvider().generate_clinical_reasoning(question, patient_context)

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            user_prompt = build_clinical_reasoning_prompt(question, patient_context)

            message = client.messages.create(
                model=self.reasoning_model,
                max_tokens=2048,
                system=CLINICAL_REASONING_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=0.0
            )

            raw_text = message.content[0].text if message.content else "{}"
            # Clean json fences if present
            clean_json = raw_text.strip()
            if clean_json.startswith("```json"):
                clean_json = clean_json[7:]
            if clean_json.endswith("```"):
                clean_json = clean_json[:-3]
            clean_json = clean_json.strip()

            parsed = json.loads(clean_json)
            return parsed
        except Exception as e:
            logger.warning(f"Live Anthropic reasoning call failed ({e}); falling back to deterministic mock.")
            return MockLLMProvider().generate_clinical_reasoning(question, patient_context)
