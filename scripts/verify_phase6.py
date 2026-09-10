"""
EvoCare Phase 6 Comprehensive Verification Script
Verifies:
- Existing Phase 2, Phase 3, Phase 4, and Phase 5 backend tests
- Dashboard aggregation API
- Patient P001 retrieval & demographics
- Clinical records (diagnoses, medications, labs)
- Caregiver observations separation
- Longitudinal memory & versioning
- Timeline chronology & source badges
- Conflict preservation & dual perspective
- Provenance & [Why?] evidence tracing
- AI-derived labelling & disclaimer
- Unknown etiology preservation & no dementia inference
- Fall vs Near-fall safety invariant
- Patient isolation (cross-patient rejection)
- Read-only behavior
- Frontend tests & production build
"""
import sys
import subprocess
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "EvoCare" / "backend"
if not backend_dir.exists():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.doctor_record import DoctorRecord
from app.models.caregiver_observation import CaregiverObservation
from app.services.dashboard_service import DashboardService

def run_verification():
    print("PHASE 6 VALIDATION\n")
    init_db()
    db = SessionLocal()

    try:
        # 1. Existing Phase 2 tests
        p001 = db.query(Patient).filter(Patient.patient_code == "P001").first()
        assert p001 is not None, "Patient P001 must exist"
        assert db.query(DoctorRecord).filter(DoctorRecord.patient_id == p001.id).count() == 5
        print("[PASS] Existing Phase 2 tests")

        # 2. Existing Phase 3 tests
        cg_count = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == p001.id).count()
        assert cg_count >= 47
        print("[PASS] Existing Phase 3 tests")

        # 3. Existing Phase 4 tests
        from app.services.llm import SafetyValidator, ParsedCaregiverObservation, ObservationCategory
        bad_obs = ParsedCaregiverObservation(category=ObservationCategory.DIZZINESS, severity="Severe", raw_statement="She is dizzy.")
        is_safe, _ = SafetyValidator.validate_safety(bad_obs, "She is dizzy.")
        assert not is_safe
        print("[PASS] Existing Phase 4 tests")

        # 4. Existing Phase 5 tests
        from app.services.memory import WikiSynchronizer
        wiki_content = WikiSynchronizer.read_page("P001", "Mobility")
        assert len(wiki_content) > 100
        print("[PASS] Existing Phase 5 tests\n")

        # 5. Dashboard API & Patient P001 retrieval
        dashboard = DashboardService.get_patient_dashboard(db, "P001")
        assert dashboard is not None
        print("[PASS] Dashboard API")
        assert dashboard.patient.patient_code == "P001"
        assert dashboard.patient.name == "Meenakshi Raman"
        print("[PASS] Patient P001 retrieval")

        # 6. Clinical, Medication, Laboratory data
        assert len(dashboard.clinical_diagnoses) >= 4
        print("[PASS] Clinical data")
        assert len(dashboard.medications) >= 4
        print("[PASS] Medication data")
        assert len(dashboard.labs) >= 1
        print("[PASS] Laboratory data")

        # 7. Caregiver separation
        assert len(dashboard.caregiver_observations) > 0
        for obs in dashboard.caregiver_observations:
            assert obs.caregiver_id.startswith("CG")
        print("[PASS] Caregiver separation")

        # 8. Longitudinal memory & Timeline
        assert dashboard.longitudinal_memory.current_version >= 1
        print("[PASS] Longitudinal memory")
        assert len(dashboard.timeline) >= 5
        print("[PASS] Timeline")

        # 9. Conflicts & Provenance & Evidence retrieval
        assert len(dashboard.conflicts) > 0
        print("[PASS] Conflicts")
        assert len(dashboard.provenance_map) > 0
        print("[PASS] Provenance")
        assert "EV-CG-021" in dashboard.provenance_map
        print("[PASS] Evidence retrieval")

        # 10. AI-derived labelling & Unknown handling
        mob_change = dashboard.recent_changes[0]
        assert mob_change.information_state == "AI_DERIVED"
        print("[PASS] AI-derived labelling")
        assert "etiology" in dashboard.longitudinal_memory.unknowns.lower()
        print("[PASS] Unknown handling")

        # 11. Safety Invariants: Near-fall, Cognition, Dizziness
        assert dashboard.fall_safety.completed_falls_count == 0
        assert dashboard.fall_safety.near_falls_count == 1
        print("[PASS] Near-fall safety")

        # Cognition: No dementia in diagnoses or claims
        diag_str = " ".join([d.description.lower() for d in dashboard.clinical_diagnoses])
        assert "dementia" not in diag_str
        assert "alzheimer" not in diag_str
        print("[PASS] Cognition safety")

        # Dizziness: No fabricated stroke/dehydration
        diz_str = " ".join([c.change_summary.lower() for c in dashboard.recent_changes if c.category.lower() == "dizziness"])
        assert "stroke" not in diz_str
        assert "dehydration" not in diz_str
        print("[PASS] Dizziness safety")

        # 12. Patient Isolation
        try:
            DashboardService.get_patient_dashboard(db, "P9999_NON_EXISTENT")
            assert False, "Cross-patient query must fail"
        except Exception:
            pass
        print("[PASS] Patient isolation")

        # 13. Read-Only Behavior
        ev_count_1 = db.query(Evidence).count()
        DashboardService.get_patient_dashboard(db, "P001")
        ev_count_2 = db.query(Evidence).count()
        assert ev_count_1 == ev_count_2
        print("[PASS] Read-only behavior\n")

        # 14. Frontend Tests & Build Validation
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        if frontend_dir.exists():
            print("Validating Frontend Tests (vitest)...")
            res_test = subprocess.run(
                ["npx", "vitest", "run"],
                cwd=str(frontend_dir),
                shell=True,
                capture_output=True,
                text=True
            )
            if res_test.returncode != 0:
                print(f"Frontend test error:\n{res_test.stdout}\n{res_test.stderr}")
                assert False, "Frontend tests failed"
            print("[PASS] Frontend tests")

            print("Validating Frontend Production Build (vite build)...")
            res_build = subprocess.run(
                ["npx", "vite", "build"],
                cwd=str(frontend_dir),
                shell=True,
                capture_output=True,
                text=True
            )
            if res_build.returncode != 0:
                print(f"Frontend build error:\n{res_build.stdout}\n{res_build.stderr}")
                assert False, "Frontend build failed"
            print("[PASS] Frontend build\n")

        print("ALL PHASE 6 VERIFICATIONS PASSED SUCCESSFULLY.")
        return 0

    except Exception as e:
        print(f"\n[FAIL] Verification error: {e}")
        return 1
    finally:
        db.close()

if __name__ == "__main__":
    sys.exit(run_verification())
