import re
import logging
from typing import Tuple, List, Dict, Any
from app.services.llm.schemas import ParsedCaregiverObservation, ObservationCategory, EventType

logger = logging.getLogger(__name__)

class SafetyValidator:
    """
    Deterministic Safety Validator for LLM-parsed caregiver observations.
    Enforces absolute healthcare and clinical data integrity invariants.
    """

    PROHIBITED_DIAGNOSES = [
        "dementia", "alzheimer", "stroke", "cerebrovascular", "parkinson",
        "hypotension", "orthostatic hypotension", "vertigo", "dehydration",
        "hypoglycemia", "anemia", "infection", "sepsis", "neuropathy",
        "transient ischemic attack", "tia", "arrhythmia"
    ]

    SEVERITY_KEYWORDS = ["mild", "moderate", "severe", "slight", "terrible", "bad", "worst", "unbearable", "little"]
    DURATION_KEYWORDS = ["second", "minute", "hour", "day", "week", "month", "all day", "brief", "short", "long"]
    ONSET_KEYWORDS = ["standing", "getting up", "morning", "night", "yesterday", "after", "while", "waking", "sudden"]
    FREQUENCY_KEYWORDS = ["times", "frequent", "often", "constantly", "rarely", "once", "twice", "recurrent", "daily"]

    @classmethod
    def validate_safety(cls, obs: ParsedCaregiverObservation, raw_text: str) -> Tuple[bool, List[str]]:
        """
        Validates safety invariants. Returns (is_safe, list_of_violations).
        """
        violations: List[str] = []
        t = raw_text.lower()

        # RULE 1: NEAR_FALL cannot become FALL
        is_near_fall_phrase = bool(re.search(r"\b(almost fell|nearly fell|slipped but caught|lost balance but caught|grabbed.*before.*fall)\b", t))
        if is_near_fall_phrase:
            if obs.category == ObservationCategory.FALL or obs.event_type == EventType.FALL or obs.ground_impact is True:
                violations.append("RULE 1 VIOLATION: Near-fall event was improperly classified as a completed FALL.")

        # If statement explicitly says "did not fall"
        if re.search(r"\b(did not fall|didn't fall|no fall)\b", t):
            if obs.category == ObservationCategory.FALL or obs.event_type == EventType.FALL or obs.ground_impact is True:
                violations.append("RULE 1 VIOLATION: Negated fall ('did not fall') was classified as a FALL.")

        # RULE 2: Caregiver confusion cannot become dementia
        if obs.dementia_diagnosed is True:
            violations.append("RULE 2 VIOLATION: Dementia was diagnosed from caregiver observation.")
        
        if obs.diagnosis:
            diag_lower = obs.diagnosis.lower()
            for prog in cls.PROHIBITED_DIAGNOSES:
                if prog in diag_lower:
                    violations.append(f"RULE 2/8 VIOLATION: Inferred clinical diagnosis '{obs.diagnosis}' is prohibited.")

        # RULE 3: Dizziness cannot receive inferred etiology
        if obs.category == ObservationCategory.DIZZINESS:
            if obs.etiology and obs.etiology.upper() not in ["UNKNOWN", "UNKNOWN (REQUIRES CLINICIAN EVALUATION)"]:
                violations.append(f"RULE 3 VIOLATION: Inferred dizziness etiology '{obs.etiology}' is prohibited. Must be UNKNOWN.")

        # Check for any prohibited diagnoses in etiology or functional impact
        for field_name, field_val in [("etiology", obs.etiology), ("functional_impact", obs.functional_impact)]:
            if field_val and field_val.upper() != "UNKNOWN":
                for prog in cls.PROHIBITED_DIAGNOSES:
                    if prog in field_val.lower():
                        violations.append(f"RULE 3 VIOLATION: Prohibited clinical condition '{prog}' found in {field_name}.")

        # RULE 4: Missing severity remains UNKNOWN
        if obs.severity and obs.severity.upper() != "UNKNOWN":
            has_severity_in_text = any(k in t for k in cls.SEVERITY_KEYWORDS)
            if not has_severity_in_text:
                violations.append(f"RULE 4 VIOLATION: Severity '{obs.severity}' was hallucinated without supporting caregiver text.")

        # RULE 5: Missing duration remains UNKNOWN
        if obs.duration and obs.duration.upper() != "UNKNOWN":
            has_duration_in_text = any(k in t for k in cls.DURATION_KEYWORDS)
            if not has_duration_in_text:
                violations.append(f"RULE 5 VIOLATION: Duration '{obs.duration}' was hallucinated without supporting caregiver text.")

        # RULE 6: Missing onset remains UNKNOWN
        if obs.onset and obs.onset.upper() != "UNKNOWN":
            has_onset_in_text = any(k in t for k in cls.ONSET_KEYWORDS)
            if not has_onset_in_text:
                violations.append(f"RULE 6 VIOLATION: Onset '{obs.onset}' was hallucinated without supporting caregiver text.")

        # RULE 7: Missing frequency remains UNKNOWN
        if obs.frequency and obs.frequency.upper() != "UNKNOWN":
            has_freq_in_text = any(k in t for k in cls.FREQUENCY_KEYWORDS)
            if not has_freq_in_text:
                violations.append(f"RULE 7 VIOLATION: Frequency '{obs.frequency}' was hallucinated without supporting caregiver text.")

        # RULE 8-12: Integrity invariant check flags
        if obs.clinical_diagnoses_inferred is True:
            violations.append("RULE 8 VIOLATION: Flag clinical_diagnoses_inferred must be False.")

        is_safe = len(violations) == 0
        if not is_safe:
            logger.warning(f"SafetyValidator rejected observation for text '{raw_text}': {violations}")

        return is_safe, violations
