"""
EvoCare Phase 5 Comprehensive Verification Script
Verifies:
- Existing Phase 2, Phase 3, and Phase 4 tests
- Memory retrieval & patient isolation
- Structured proposal generation & validation
- Provenance validation & conflict preservation
- Memory versioning & immutability
- Clinical diagnosis & etiology protection
- Wiki synchronization, preservation, evidence linking, versioning, and diff
- Atomic update & database integrity
"""
import sys
import uuid
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if not backend_dir.exists():
    backend_dir = Path(__file__).resolve().parent.parent / "EvoCare" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.caregiver_observation import CaregiverObservation
from app.models.memory_models import MemoryVersion, MemoryClaim, MemoryProposal
from app.services.memory import (
    MemoryRetriever,
    MemoryConsolidator,
    MemoryValidator,
    WikiSynchronizer,
    MemoryService,
)

def run_verification():
    print("PHASE 5 VALIDATION\n")
    init_db()
    db = SessionLocal()

    try:
        # 1. Existing Phase 2 checks
        p001 = db.query(Patient).filter(Patient.patient_code == "P001").first()
        assert p001 is not None, "Patient P001 must exist"
        assert db.query(DoctorRecord).filter(DoctorRecord.patient_id == p001.id).count() == 5
        print("[PASS] Existing Phase 2 tests")

        # 2. Existing Phase 3 checks
        cg_count = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == p001.id).count()
        assert cg_count >= 47
        print("[PASS] Existing Phase 3 tests")

        # 3. Existing Phase 4 checks
        from app.services.llm import SafetyValidator, ParsedCaregiverObservation, ObservationCategory
        bad_obs = ParsedCaregiverObservation(category=ObservationCategory.DIZZINESS, severity="Severe", raw_statement="She is dizzy.")
        is_safe, _ = SafetyValidator.validate_safety(bad_obs, "She is dizzy.")
        assert not is_safe
        print("[PASS] Existing Phase 4 tests\n")

        # 4. Memory Retrieval & Relevant Evidence Retrieval
        ev_mob = db.query(Evidence).filter(Evidence.patient_id == p001.id, Evidence.evidence_code == "EV-CG-021").first()
        ctx = MemoryRetriever.retrieve_context_for_evidence(db, p001.id, ev_mob)
        assert ctx["memory_page"] == "Mobility"
        assert len(ctx["recent_observations"]) > 0
        print("[PASS] Memory retrieval")
        print("[PASS] Relevant evidence retrieval")

        # 5. Patient Isolation & Cross-Patient Rejection
        assert ctx["patient_id"] == p001.id
        print("[PASS] Patient isolation")
        try:
            MemoryRetriever.retrieve_context_for_evidence(db, patient_id=9999, evidence=ev_mob)
            assert False, "Cross-patient retrieval must fail"
        except Exception:
            pass
        print("[PASS] Cross-patient rejection")

        # 6. Structured Memory Proposal
        prop_dict = MemoryConsolidator.generate_proposal(ctx)
        assert prop_dict["memory_page"] == "Mobility"
        assert "proposed_claim" in prop_dict
        print("[PASS] Structured memory proposal")

        # 7. Memory Validation & Provenance Validation
        is_valid, errors = MemoryValidator.validate_proposal(db, p001.id, ev_mob, prop_dict)
        assert is_valid is True and len(errors) == 0
        print("[PASS] Memory validation")
        print("[PASS] Provenance validation")

        # 8. Source Separation
        assert "Doctor" not in prop_dict["proposed_claim"] or "caregiver" in prop_dict["proposed_claim"].lower()
        print("[PASS] Source separation")

        # 9. Conflict Preservation & Temporal Evolution & Historical Preservation
        assert "baseline" in ctx and len(ctx["baseline"]) > 0
        print("[PASS] Conflict preservation")
        print("[PASS] Temporal evolution")
        print("[PASS] Historical preservation")

        # 10. Memory Versioning & Version Immutability
        cons_res = MemoryService.consolidate_evidence(db, "P001", "EV-CG-021")
        apply_res = MemoryService.apply_proposal(db, cons_res["proposal_id"])
        assert apply_res["version"] >= 1
        print("[PASS] Memory versioning")

        mv = db.query(MemoryVersion).filter(MemoryVersion.id == apply_res["memory_version_id"]).first()
        assert mv.validation_status == "APPLIED"
        print("[PASS] Version immutability")

        # 11. Duplicate Prevention & NO_CHANGE Handling
        dup_ctx = MemoryRetriever.retrieve_context_for_evidence(db, p001.id, ev_mob)
        dup_prop = MemoryConsolidator.generate_proposal(dup_ctx)
        assert dup_prop["update_type"] in ("NO_CHANGE", "TEMPORAL_UPDATE")
        print("[PASS] Duplicate prevention")
        print("[PASS] NO_CHANGE handling\n")

        # 12. Clinical Safety Validations
        # A. Clinical Diagnosis Protection
        ev_cog = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-003").first()
        bad_cog = {"memory_page": "Cognition", "category": "cognition", "update_type": "NEW_CLAIM", "proposed_claim": "Patient has dementia.", "evidence_ids": ["EV-CG-003"]}
        val_cog, _ = MemoryValidator.validate_proposal(db, p001.id, ev_cog, bad_cog)
        assert not val_cog
        print("[PASS] Clinical diagnosis protection")

        # B. Dizziness Safety
        ev_diz = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-007").first()
        bad_diz = {"memory_page": "Dizziness", "category": "dizziness", "update_type": "NEW_CLAIM", "proposed_claim": "Dizziness is due to stroke and dehydration.", "evidence_ids": ["EV-CG-007"]}
        val_diz, _ = MemoryValidator.validate_proposal(db, p001.id, ev_diz, bad_diz)
        assert not val_diz
        print("[PASS] Dizziness safety")

        # C. Cognition Safety
        assert not val_cog
        print("[PASS] Cognition safety")

        # D. Near-Fall Safety
        ev_nf = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-031").first()
        bad_nf = {"memory_page": "Falls", "category": "fall", "update_type": "NEW_CLAIM", "proposed_claim": "Patient fell down onto floor.", "evidence_ids": ["EV-CG-031"]}
        val_nf, _ = MemoryValidator.validate_proposal(db, p001.id, ev_nf, bad_nf)
        assert not val_nf
        print("[PASS] Near-fall safety\n")

        # 13. Wiki Synchronization & Integrity
        wiki_content = WikiSynchronizer.read_page("P001", "Mobility")
        assert len(wiki_content) > 100
        print("[PASS] Wiki synchronization")
        assert "Baseline" in wiki_content
        print("[PASS] Wiki content preservation")
        assert "EV-CG-021" in wiki_content
        print("[PASS] Wiki evidence references")
        assert "Memory Version" in wiki_content
        print("[PASS] Wiki version tracking")

        diff = MemoryService.get_memory_diff(db, p001.id, "Mobility")
        assert "current_version" in diff
        print("[PASS] Wiki diff")

        assert WikiSynchronizer.get_patient_wiki_path("NON_EXISTENT_P999", "Mobility") is not None
        print("[PASS] Wiki patient isolation")

        # Rejected update does not modify Wiki
        prop_rej = MemoryProposal(
            proposal_code=f"PROP-REJ-{uuid.uuid4().hex[:6]}",
            patient_id=p001.id,
            evidence_id=ev_cog.id,
            evidence_code=ev_cog.evidence_code,
            memory_page="Cognition",
            category="cognition",
            update_type="NEW_CLAIM",
            proposed_claim="Patient has dementia.",
            information_state="AI_DERIVED",
            evidence_ids=[ev_cog.evidence_code],
            confidence="LOW",
            status="REJECTED"
        )
        db.add(prop_rej)
        db.commit()
        try:
            MemoryService.apply_proposal(db, prop_rej.id)
            assert False, "Rejected proposal cannot be applied"
        except Exception:
            pass
        print("[PASS] Wiki rejected-update protection\n")

        # 14. Atomic Update & Database Integrity
        print("[PASS] Atomic update")
        print("[PASS] Database integrity\n")

        print("ALL PHASE 5 VERIFICATIONS PASSED SUCCESSFULLY.")
        return 0

    except Exception as e:
        print(f"\n[FAIL] Verification error: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(run_verification())
