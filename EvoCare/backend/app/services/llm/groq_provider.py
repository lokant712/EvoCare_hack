import json
import logging
from typing import Dict, Any, Optional, List
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

import time

logger = logging.getLogger(__name__)


class GroqProvider(LLMProvider):
    """
    Groq LLM Provider with internal model failover & rate-limit circuit breaker:
      - Primary Model: openai/gpt-oss-120b
      - Fallback Model: openai/gpt-oss-20b
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        primary_model: Optional[str] = None,
        fallback_model: Optional[str] = None,
        enabled: Optional[bool] = None
    ):
        self.api_key = api_key if api_key is not None else settings.GROQ_API_KEY
        self.primary_model = primary_model if primary_model is not None else getattr(settings, "GROQ_PRIMARY_MODEL", "openai/gpt-oss-120b")
        self.fallback_model = fallback_model if fallback_model is not None else getattr(settings, "GROQ_FALLBACK_MODEL", "openai/gpt-oss-20b")
        self.enabled = enabled if enabled is not None else settings.LLM_ENABLED
        self.primary_rate_limited_until: float = 0.0

    def is_configured(self) -> bool:
        return bool(self.enabled and self.api_key and self.api_key.strip())

    def _call_groq_completion(self, client: Any, user_prompt: str, system_prompt: str) -> tuple[str, str]:
        """
        Attempts primary model first (openai/gpt-oss-120b);
        automatically fails over to fallback model (openai/gpt-oss-20b) if rate-limited or error.
        Returns: (raw_text, model_used)
        """
        # If primary model is in active rate-limit cool-down, go directly to fallback model
        if time.time() < self.primary_rate_limited_until:
            rem = int(self.primary_rate_limited_until - time.time())
            logger.info(f"Groq primary model ({self.primary_model}) in cool-down ({rem}s left). Routing to fallback model ({self.fallback_model}).")
            models_to_try = [self.fallback_model]
        else:
            models_to_try = [self.primary_model, self.fallback_model]

        last_exception = None

        for model in models_to_try:
            try:
                logger.info(f"Calling Groq model: {model}...")
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.0,
                    response_format={"type": "json_object"}
                )
                raw_text = response.choices[0].message.content or ""
                logger.info(f"Groq model {model} completed successfully.")
                return raw_text, model
            except Exception as e:
                err_str = str(e)
                if model == self.primary_model and ("429" in err_str or "rate" in err_str.lower() or "limit" in err_str.lower()):
                    self.primary_rate_limited_until = time.time() + 60.0
                    logger.warning(f"Groq primary model {model} rate limited (429). Activated 60s circuit breaker.")
                logger.warning(f"Groq model {model} failed ({type(e).__name__}: {e}). Trying next model if available...")
                last_exception = e

        raise last_exception or RuntimeError("All Groq models failed")

    def extract_observation(self, text: str, patient_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        if not self.is_configured():
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="GROQ_API_KEY is not configured or LLM is disabled",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            from groq import Groq
        except ImportError:
            logger.warning("groq package is not installed in the environment")
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message="groq package not installed",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        try:
            client = Groq(api_key=self.api_key)
            user_prompt = build_extraction_prompt(text, patient_context)
            raw_response, used_model = self._call_groq_completion(client, user_prompt, SYSTEM_PROMPT)
        except Exception as e:
            logger.warning(f"Groq observation extraction failed across all models: {e}")
            return LLMResult(
                status=LLMStatus.ERROR,
                error_message=f"Groq API error: {str(e)}",
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
        Calls Groq with primary model (openai/gpt-oss-120b) and fallback (openai/gpt-oss-20b).
        Raises on failure so the multi-tier orchestrator can transition to offline mock.
        """
        if not self.is_configured():
            raise RuntimeError("Groq API key is not configured or LLM is disabled")

        from groq import Groq

        client = Groq(api_key=self.api_key)
        user_prompt = build_clinical_reasoning_prompt(question, patient_context)

        raw_text, used_model = self._call_groq_completion(client, user_prompt, CLINICAL_REASONING_SYSTEM_PROMPT)

        clean_json = raw_text.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed = json.loads(clean_json)
        parsed["_llm_model_used"] = f"Groq ({used_model})"
        return parsed
