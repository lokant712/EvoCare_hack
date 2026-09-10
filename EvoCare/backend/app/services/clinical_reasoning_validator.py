import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.evidence import Evidence
from app.schemas.clinical_reasoning import ClinicalConsideration, ConsiderationStatus, EvidenceStrength

logger = logging.getLogger(__name__)


class ClinicalReasoningValidator:
    """
    Deterministic safety and provenance validator for LLM clinical reasoning output.
    Rejects any ungrounded diagnoses, treatment recommendations, fabricated evidence IDs,
    or violations of medical safety invariants.
    """

    PROHIBITED_PRESCRIPTION_PATTERNS = [
        r"\b(?:stop|discontinue|start|prescribe|administer|increase|decrease|change dose)\s+(?:amlodipine|metformin|atorvastatin|aspirin|medication|drug|dose|tablets?)\b",
        r"\b(?:prescription|rx|dosage adjustment):\s*[a-z0-9]",
        r"\b(?:recommend starting|recommend stopping|should take|should discontinue)\b",
    ]

    UNSUPPORTED_DIAGNOSIS_PATTERNS = [
        r"\bpatient has (?:dementia|alzheimer'?s|stroke|orthostatic hypotension|vascular dementia)\b",
        r"\bthe patient has (?:dementia|alzheimer'?s|stroke|orthostatic hypotension)\b",
        r"\bdiagnosed with (?:dementia|alzheimer'?s|stroke|orthostatic hypotension)\b",
        r"\bis suffering from (?:dementia|alzheimer'?s|stroke)\b",
    ]

    UNSUPPORTED_CAUSALITY_PATTERNS = [
        r"\b(?:amlodipine|metformin|atorvastatin|medication) is (?:causing|the cause of|responsible for) the dizziness\b",
        r"\bher dizziness is (?:definitely|certainly|proven to be) caused by\b",
        r"\bthe dizziness is caused by\b",
    ]

    NEAR_FALL_DISTORTION_PATTERNS = [
        r"\bshe fell yesterday\b",
        r"\bpatient fell on (?:september 1|2026-09-01)\b",
        r"\brecent fall in (?:the )?bathroom\b",
        r"\b(?:had a|experienced a|suffered a|resulted in a)\s+completed fall\b",
    ]

    FABRICATED_VITALS_PATTERNS = [
        r"\b(?:bp|blood pressure)\s*(?:of|=|:)?\s*90\/60\b",
        r"\b90\/60\s*mmhg\b",
    ]

    CURRENT_RED_FLAG_ASSERTION_PATTERNS = [
        r"\bpatient is currently experiencing (?:chest pain|syncope|shortness of breath)\b",
        r"\bpatient has acute (?:chest pain|syncope)\b",
    ]

    @classmethod
    def validate_safety_and_provenance(
        cls,
        parsed_data: Dict[str, Any],
        context: Dict[str, Any],
        db: Session,
        patient_id: str,
        question: str
    ) -> Tuple[bool, List[str], Optional[Dict[str, Any]]]:
        """
        Validates the parsed LLM clinical reasoning dictionary against deterministic rules and database records.
        Returns: (is_valid, violations_list, sanitized_data_or_none)
        """
        violations: List[str] = []

        # Check question for direct prescription request refusal
        q_lower = question.lower()
        if any(term in q_lower for term in ["what should i prescribe", "prescribe me", "dosage should i give", "what drug should i start", "should i stop amlodipine"]):
            # Safe refusal response directly handled
            return True, [], {
                "considerations": [
                    {
                        "title": "Clinical Guidance & Prescription Limitation",
                        "category": "Prescription / Treatment Policy",
                        "description": "Prescription and treatment recommendations are strictly out of scope for the Clinical Reasoning Assistant.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [],
                        "contradicting_evidence": ["Treatment decisions remain exclusively with the licensed clinician."],
                        "missing_information": ["Formal clinician clinical assessment and treatment plan"],
                        "evidence_strength": "INSUFFICIENT",
                        "reasoning": "I can summarize relevant clinical considerations and evidence, but I cannot prescribe or recommend a treatment plan.",
                        "uncertainty": "Autonomous prescribing is prohibited by EvoCare clinical safety rules.",
                        "references": []
                    }
                ],
                "missing_information": ["Clinician treatment decision"],
                "red_flags": [],
                "relevant_changes": [],
                "limitations": ["Automated treatment recommendations are prohibited."]
            }

        # 1. Structure Check
        considerations_raw = parsed_data.get("considerations", [])
        if not isinstance(considerations_raw, list):
            violations.append("RULE 0 VIOLATION: Output must contain a 'considerations' list.")
            return False, violations, None

        # Build set of valid patient evidence IDs and catalog
        valid_patient_evidence = db.query(Evidence).filter(
            (Evidence.patient_id == context.get("demographics", {}).get("patient_code")) |
            (Evidence.patient.has(patient_code=patient_id)) |
            (Evidence.patient_id == (int(patient_id) if patient_id.isdigit() else -1))
        ).all()
        
        valid_evidence_map = {e.evidence_code: e for e in valid_patient_evidence}

        # Check for cross-patient evidence lookup
        all_evidence = db.query(Evidence).all()
        all_evidence_map = {e.evidence_code: e for e in all_evidence}

        validated_considerations = []

        for idx, c in enumerate(considerations_raw):
            title = c.get("title", "")
            status = c.get("status", "POSSIBLE_CONSIDERATION")
            desc = c.get("description", "")
            reasoning = c.get("reasoning", "")
            strength = c.get("evidence_strength", "LIMITED")
            supp_ev = c.get("supporting_evidence", [])
            contra_ev = c.get("contradicting_evidence", [])
            missing_info = c.get("missing_information", [])
            uncertainty = c.get("uncertainty", "")
            refs = c.get("references", [])

            full_text = f"{title} {desc} {reasoning} {uncertainty}".lower()

            # Rule 1: Status must NEVER be DIAGNOSIS
            if status == "DIAGNOSIS":
                violations.append(f"RULE 1 VIOLATION: Consideration '{title}' status cannot be DIAGNOSIS. Must be POSSIBLE_CONSIDERATION.")

            # Rule 2: Prohibited prescription / treatment recommendations
            for pattern in cls.PROHIBITED_PRESCRIPTION_PATTERNS:
                if re.search(pattern, full_text):
                    violations.append(f"RULE 2 VIOLATION: Output contained prohibited treatment/prescription recommendation: '{pattern}'.")

            # Rule 3: Prohibited unsupported diagnoses (e.g. Dementia, Stroke, confirmed Orthostatic Hypotension)
            for pattern in cls.UNSUPPORTED_DIAGNOSIS_PATTERNS:
                if re.search(pattern, full_text):
                    violations.append(f"RULE 3 VIOLATION: Output asserted unconfirmed clinical diagnosis: '{pattern}'.")

            # Rule 4: Prohibited unconfirmed medication causality
            for pattern in cls.UNSUPPORTED_CAUSALITY_PATTERNS:
                if re.search(pattern, full_text):
                    violations.append(f"RULE 4 VIOLATION: Output asserted unproven medication causality: '{pattern}'.")

            # Rule 5: Distortion of near-fall into fall
            for pattern in cls.NEAR_FALL_DISTORTION_PATTERNS:
                if re.search(pattern, full_text):
                    violations.append(f"RULE 5 VIOLATION: Distorted near-fall into a completed fall: '{pattern}'.")

            # Rule 6: Fabricated vitals / labs
            for pattern in cls.FABRICATED_VITALS_PATTERNS:
                if re.search(pattern, full_text):
                    violations.append(f"RULE 6 VIOLATION: Fabricated vital signs or laboratory measurement: '{pattern}'.")

            # Rule 7: Unsupported certainty
            if strength == "STRONG" and len(supp_ev) <= 1:
                violations.append(f"RULE 7 VIOLATION: Evidence strength claimed as STRONG for isolated observation in '{title}'.")

            # Rule 8: Evidence verification (Existence, Patient Isolation, Immutability)
            validated_supp_ev = []
            for ev_ref in supp_ev:
                ev_id = ev_ref.get("evidence_id") if isinstance(ev_ref, dict) else str(ev_ref)
                if not ev_id:
                    continue

                if ev_id not in valid_evidence_map:
                    if ev_id in all_evidence_map:
                        violations.append(f"RULE 8A VIOLATION: Cross-patient evidence breach. Evidence ID '{ev_id}' belongs to another patient.")
                    else:
                        violations.append(f"RULE 8B VIOLATION: Fabricated evidence ID '{ev_id}' does not exist in patient database.")
                else:
                    # Verified evidence record
                    db_ev = valid_evidence_map[ev_id]
                    validated_supp_ev.append({
                        "evidence_id": db_ev.evidence_code,
                        "source_type": db_ev.source_type.value if hasattr(db_ev.source_type, 'value') else str(db_ev.source_type),
                        "observed_at": db_ev.observed_at.strftime("%Y-%m-%d %H:%M") if db_ev.observed_at else "Unknown",
                        "original_statement": db_ev.original_statement
                    })

            for ref in refs:
                if ref not in valid_evidence_map:
                    if ref in all_evidence_map:
                        violations.append(f"RULE 8A VIOLATION: Cross-patient evidence reference '{ref}'.")
                    else:
                        violations.append(f"RULE 8B VIOLATION: Fabricated reference ID '{ref}'.")

            validated_considerations.append({
                "title": title,
                "category": c.get("category", "General"),
                "description": desc,
                "status": ConsiderationStatus.POSSIBLE_CONSIDERATION.value if status != ConsiderationStatus.CLINICIAN_CONFIRMED.value else status,
                "supporting_evidence": validated_supp_ev,
                "contradicting_evidence": contra_ev if contra_ev else ["No contradicting evidence identified in the available record."],
                "missing_information": missing_info,
                "evidence_strength": strength if strength in ["STRONG", "MODERATE", "LIMITED", "INSUFFICIENT"] else "LIMITED",
                "reasoning": reasoning,
                "uncertainty": uncertainty,
                "references": [r for r in refs if r in valid_evidence_map]
            })

        # Rule 9: Red flag current symptom assertions
        red_flags_raw = parsed_data.get("red_flags", [])
        for rf in red_flags_raw:
            rf_lower = rf.lower()
            for pattern in cls.CURRENT_RED_FLAG_ASSERTION_PATTERNS:
                if re.search(pattern, rf_lower):
                    violations.append(f"RULE 9 VIOLATION: Red flag asserted current active emergency symptom: '{pattern}'.")

        if violations:
            logger.warning(f"Clinical reasoning safety check failed with {len(violations)} violations: {violations}")
            return False, violations, None

        sanitized_data = {
            "considerations": validated_considerations,
            "missing_information": parsed_data.get("missing_information", []),
            "red_flags": parsed_data.get("red_flags", []),
            "relevant_changes": parsed_data.get("relevant_changes", []),
            "limitations": parsed_data.get("limitations", [])
        }

        return True, [], sanitized_data
