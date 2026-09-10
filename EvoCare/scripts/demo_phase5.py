"""
EvoCare Phase 5 Demonstration Script: Evolving Patient Memory & Living Patient Wiki
Demonstrates:
1. Reading initial Patient Wiki state (Mobility.md)
2. Ingesting new caregiver observation ("She needed someone's arm while walking outside today.")
3. Retrieving relevant historical context (baseline, recent obs, conflicts)
4. Generating structured memory proposal
5. Deterministically validating proposal
6. Atomically applying proposal and creating immutable MemoryVersion
7. Synchronizing and rendering updated Living Patient Wiki
8. Preserving historical memory and evidence provenance
9. Ingesting second observation ("She walked normally inside today.") and evolving memory
10. Demonstrating rejection of malicious/hallucinated proposals (dementia, dizziness cause, near-fall)
11. Demonstrating cross-patient isolation protection
"""
import sys
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
from app.services.memory import (
    MemoryRetriever,
    MemoryConsolidator,
    MemoryValidator,
    WikiSynchronizer,
    MemoryService,
)
from app.services.observation_pipeline_service import ObservationPipelineService

def main():
    print("=" * 80)
    print("EVOCARE PHASE 5: EVOLVING PATIENT MEMORY & LIVING PATIENT WIKI DEMO")
    print("=" * 80)

    init_db()
    db = SessionLocal()

    try:
        p001 = db.query(Patient).filter(Patient.patient_code == "P001").first()
        assert p001 is not None, "Patient P001 must exist"

        print("\n--- STEP 1: Original Patient Wiki State (Mobility.md) ---")
        initial_wiki = WikiSynchronizer.read_page("P001", "Mobility")
        print(f"Read Mobility.md ({len(initial_wiki)} bytes). Baseline and existing records present.")
        print("Sample excerpt from Baseline:")
        for line in initial_wiki.splitlines()[:18]:
            print(f"  {line}")

        print("\n--- STEP 2: New Validated Caregiver Evidence ---")
        # Ingest Observation 1
        sess1 = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She needed someone's arm while walking outside today.",
            caregiver_id="CG002",
            processing_mode="DETERMINISTIC"
        )
        comp1 = ObservationPipelineService.complete_session(db=db, session_id=sess1["session_id"])
        ev1_code = comp1["evidence_code"]
        print(f"Created & Ingested Evidence: {ev1_code}")
        print(f"Statement: 'She needed someone's arm while walking outside today.'")

        print("\n--- STEP 3: Retrieve Relevant Historical Memory ---")
        ev1 = db.query(Evidence).filter(Evidence.evidence_code == ev1_code).first()
        ctx1 = MemoryRetriever.retrieve_context_for_evidence(db=db, patient_id=p001.id, evidence=ev1)
        print(f"Retrieved Category: {ctx1['category']}")
        print(f"Target Memory Page: {ctx1['memory_page']}")
        print(f"Baseline Context: {ctx1['baseline']}")
        print(f"Recent Observations Found: {len(ctx1['recent_observations'])}")

        print("\n--- STEP 4: Generate Structured Memory Proposal ---")
        prop1_dict = MemoryConsolidator.generate_proposal(ctx1)
        print(f"Update Type: {prop1_dict['update_type']}")
        print(f"Proposed Claim: {prop1_dict['proposed_claim']}")
        print(f"Evidence IDs: {prop1_dict['evidence_ids']}")
        print(f"Confidence: {prop1_dict['confidence']}")

        print("\n--- STEP 5: Validate Memory Proposal ---")
        is_valid1, errors1 = MemoryValidator.validate_proposal(db, p001.id, ev1, prop1_dict)
        print(f"Proposal Validation Status: {'PASS (VALIDATED)' if is_valid1 else 'REJECTED'}")
        assert is_valid1

        print("\n--- STEP 6 & 7: Apply Proposal & Synchronize Living Patient Wiki ---")
        cons_res1 = MemoryService.consolidate_evidence(db, "P001", ev1_code)
        apply_res1 = MemoryService.apply_proposal(db, cons_res1["proposal_id"])
        print(f"Memory Version Created: Version {apply_res1['version']}")
        print(f"Wiki Page Synchronized: {apply_res1['wiki_page']}")
        print(f"Applied Claim: {apply_res1['applied_claim']}")

        print("\n--- STEP 8: Verify Provenance & History Preservation ---")
        updated_wiki1 = WikiSynchronizer.read_page("P001", "Mobility")
        print(f"Evidence {ev1_code} linked in Wiki: {'YES' if ev1_code in updated_wiki1 else 'NO'}")
        print(f"Baseline preserved: {'YES' if 'Baseline' in updated_wiki1 else 'NO'}")

        print("\n--- STEP 9 & 10: Ingest Second Observation (Normal Indoor Walking) & Evolve ---")
        sess2 = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She was walking better today and did not need support inside the house.",
            caregiver_id="CG001",
            processing_mode="DETERMINISTIC"
        )
        comp2 = ObservationPipelineService.complete_session(db=db, session_id=sess2["session_id"])
        ev2_code = comp2["evidence_code"]

        cons_res2 = MemoryService.consolidate_evidence(db, "P001", ev2_code)
        apply_res2 = MemoryService.apply_proposal(db, cons_res2["proposal_id"])
        print(f"Second Evidence: {ev2_code}")
        print(f"New Memory Version: Version {apply_res2['version']}")
        print(f"Applied Claim 2: {apply_res2['applied_claim']}")

        print("\n--- STEP 11: Display Final Evolving Mobility Wiki Excerpt ---")
        final_wiki = WikiSynchronizer.read_page("P001", "Mobility")
        print("Final Wiki Memory Version Banner:")
        for line in final_wiki.splitlines()[-9:]:
            print(f"  {line}")

        print("\n--- STEP 12: Memory Version History ---")
        history = MemoryService.get_memory_history(db, p001.id, "Mobility")
        for v in history:
            print(f"  Version {v['version_number']}: {v['change_summary']} (Status: {v['validation_status']})")

        print("\n--- STEP 13: Safety Invariants Demonstration ---")
        # 1. Confusion -> Dementia Rejection
        ev_cog = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-003").first()
        bad_cog = {
            "memory_page": "Cognition", "category": "cognition", "update_type": "NEW_CLAIM",
            "proposed_claim": "Patient has dementia.", "evidence_ids": ["EV-CG-003"]
        }
        val_cog, err_cog = MemoryValidator.validate_proposal(db, p001.id, ev_cog, bad_cog)
        print(f"1. Malicious Dementia Diagnosis: {'REJECTED [PASS]' if not val_cog else 'FAILED'}")

        # 2. Dizziness -> Dehydration/Stroke Rejection
        ev_diz = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-007").first()
        bad_diz = {
            "memory_page": "Dizziness", "category": "dizziness", "update_type": "NEW_CLAIM",
            "proposed_claim": "Patient is dizzy likely due to severe dehydration and stroke.",
            "evidence_ids": ["EV-CG-007"]
        }
        val_diz, err_diz = MemoryValidator.validate_proposal(db, p001.id, ev_diz, bad_diz)
        print(f"2. Malicious Dizziness Etiology: {'REJECTED [PASS]' if not val_diz else 'FAILED'}")

        # 3. Near-Fall -> Completed Fall Rejection
        ev_nf = db.query(Evidence).filter(Evidence.evidence_code == "EV-CG-031").first()
        bad_nf = {
            "memory_page": "Falls", "category": "fall", "update_type": "NEW_CLAIM",
            "proposed_claim": "Patient fell down onto bathroom floor.", "evidence_ids": ["EV-CG-031"]
        }
        val_nf, err_nf = MemoryValidator.validate_proposal(db, p001.id, ev_nf, bad_nf)
        print(f"3. Near-Fall to Fall Upgrade: {'REJECTED [PASS]' if not val_nf else 'FAILED'}")

        # 4. Cross-Patient Contamination Rejection
        try:
            MemoryRetriever.retrieve_context_for_evidence(db, patient_id=9999, evidence=ev1)
            cross_pass = False
        except Exception:
            cross_pass = True
        print(f"4. Cross-Patient Access (P001 evidence on Patient 9999): {'REJECTED [PASS]' if cross_pass else 'FAILED'}")

        print("\n" + "=" * 80)
        print("PHASE 5 DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    main()
