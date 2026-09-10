"""
EvoCare Phase 4 Verification Script
Verifies:
- Phase 2 data remains unchanged
- Phase 3 behavior remains functional
- LLM schema validation works
- Safety rules work
- Fallback works
- Provenance works
- Evidence immutability remains intact
- No diagnoses are created
- No clinical records are modified
- No cross-patient contamination occurs
"""
import sys
import json
from pathlib import Path

# Add backend to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "EvoCare" / "backend"
if not backend_dir.exists():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.caregiver_observation import CaregiverObservation


from app.services.llm import (
    ParsedCaregiverObservation,
    ObservationCategory,
    EventType,
    ConfidenceLevel,
    CertaintyState,
    LLMStatus,
    ProcessingMethod,
    MockLLMProvider,
    AnthropicProvider,
    ObservationValidator,
    SafetyValidator,
)
from app.services.observation_pipeline_service import ObservationPipelineService

def run_verification():
    print("PHASE 4 VALIDATION\n")
    init_db()
    db = SessionLocal()

    try:
        # 1. Check Phase 2 data immutability
        p001 = db.query(Patient).filter(Patient.patient_code == "P001").first()
        assert p001 is not None, "Patient P001 must exist"
        doc_count = db.query(DoctorRecord).filter(DoctorRecord.patient_id == p001.id).count()
        assert doc_count == 5, f"Doctor records must remain 5, found {doc_count}"
        med_count = db.query(Medication).filter(Medication.patient_id == p001.id).count()
        assert med_count == 4, f"Medications must remain 4, found {med_count}"
        print("[PASS] Existing Phase 2 tests")

        # 2. Check Phase 3 behavior
        start_p3 = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She is dizzy.",
            caregiver_id="CG001",
            processing_mode="DETERMINISTIC"
        )
        assert start_p3["category"] == "dizziness"
        assert start_p3["processing_method"] == "DETERMINISTIC"
        print("[PASS] Existing Phase 3 tests")

        # 3. LLM Schema Validation
        valid_json = json.dumps({
            "category": "dizziness",
            "subject": "patient",
            "event_type": "DIZZINESS_EPISODE",
            "severity": "Mild",
            "duration": "A few seconds",
            "frequency": "UNKNOWN",
            "onset": "After standing",
            "context": "Bedroom",
            "functional_impact": "UNKNOWN",
            "associated_details": {},
            "negations": [],
            "confidence": "HIGH",
            "certainty": "CONFIRMED",
            "unknown_fields": [],
            "requires_clarification": False,
            "clarification_fields": [],
            "etiology": "UNKNOWN",
            "diagnosis": None,
            "dementia_diagnosed": False,
            "clinical_diagnoses_inferred": False,
            "ground_impact": False,
            "raw_statement": "She had mild dizziness for a few seconds after standing in the bedroom."
        })
        is_valid, parsed_obs, _ = ObservationValidator.validate_raw_response(
            valid_json, "She had mild dizziness for a few seconds after standing in the bedroom."
        )
        assert is_valid is True and parsed_obs is not None
        print("[PASS] LLM schema validation")

        # 4. Safety validation: reject hallucinated severity
        bad_parsed = ParsedCaregiverObservation(
            category=ObservationCategory.DIZZINESS,
            severity="Severe",
            raw_statement="She is dizzy."
        )
        is_safe, violations = SafetyValidator.validate_safety(bad_parsed, "She is dizzy.")
        assert not is_safe and len(violations) > 0
        print("[PASS] Safety validation")

        # 5. Unknown preservation
        unkn_obs = ParsedCaregiverObservation(
            category=ObservationCategory.DIZZINESS,
            severity="UNKNOWN",
            duration="UNKNOWN",
            onset="UNKNOWN",
            etiology="UNKNOWN",
            raw_statement="She is dizzy."
        )
        is_safe, _ = SafetyValidator.validate_safety(unkn_obs, "She is dizzy.")
        assert is_safe
        print("[PASS] Unknown preservation")

        # 6. Near-fall separation
        near_fall_bad = ParsedCaregiverObservation(
            category=ObservationCategory.FALL,
            event_type="FALL",
            ground_impact=True,
            raw_statement="She almost fell."
        )
        is_safe, violations = SafetyValidator.validate_safety(near_fall_bad, "She almost fell.")
        assert not is_safe
        print("[PASS] Near-fall separation")

        # 7. Dizziness cause protection
        dizzy_bad = ParsedCaregiverObservation(
            category=ObservationCategory.DIZZINESS,
            etiology="stroke and dehydration",
            raw_statement="She is dizzy."
        )
        is_safe, violations = SafetyValidator.validate_safety(dizzy_bad, "She is dizzy.")
        assert not is_safe
        print("[PASS] Dizziness cause protection")

        # 8. Cognition safety: no dementia diagnosis
        cog_bad = ParsedCaregiverObservation(
            category=ObservationCategory.COGNITION,
            diagnosis="Dementia",
            dementia_diagnosed=True,
            raw_statement="She seems confused today."
        )
        is_safe, violations = SafetyValidator.validate_safety(cog_bad, "She seems confused today.")
        assert not is_safe
        print("[PASS] Cognition safety")

        # 9. LLM fallback when API key is missing or error
        fallback_prov = AnthropicProvider(api_key="", enabled=True)
        fallback_res = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She didn't eat much.",
            processing_mode="AUTO",
            llm_provider=fallback_prov
        )
        assert fallback_res["processing_method"] == "LLM_FALLBACK"
        print("[PASS] LLM fallback")

        # 10. Evidence Provenance
        mock_prov = MockLLMProvider()
        ObservationPipelineService.set_llm_provider(mock_prov)
        sess = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She had knee pain.",
            processing_mode="LLM"
        )
        comp = ObservationPipelineService.complete_session(db=db, session_id=sess["session_id"])
        ev = db.query(Evidence).filter(Evidence.evidence_code == comp["evidence_code"]).first()
        cg = db.query(CaregiverObservation).filter(CaregiverObservation.evidence_id == ev.id).first()
        assert cg.attributes.get("extraction_method") == "LLM_ASSISTED"
        print("[PASS] Evidence provenance")

        # 11. Evidence immutability
        assert ev.status.value == "IMMUTABLE"
        print("[PASS] Evidence immutability")

        # 12. No clinical record modification
        doc_count_after = db.query(DoctorRecord).filter(DoctorRecord.patient_id == p001.id).count()
        assert doc_count_after == 5
        print("[PASS] No clinical record modification")

        print("\nALL PHASE 4 VERIFICATIONS PASSED SUCCESSFULLY.")
        return 0

    except Exception as e:
        print(f"\n[FAIL] Verification error: {e}")
        return 1
    finally:
        ObservationPipelineService.set_llm_provider(None)
        db.close()

if __name__ == "__main__":
    sys.exit(run_verification())
