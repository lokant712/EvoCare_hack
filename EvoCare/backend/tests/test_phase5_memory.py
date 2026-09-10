import pytest
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.memory_models import MemoryVersion, MemoryClaim, MemoryProposal
from app.services.memory import (
    MemoryRetriever,
    MemoryConsolidator,
    MemoryValidator,
    MemoryService,
)

def test_memory_retrieval_same_patient(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-021").first()
    assert ev is not None

    ctx = MemoryRetriever.retrieve_context_for_evidence(db_session, p.id, ev)
    assert ctx["patient_id"] == p.id
    assert ctx["category"] == "mobility"
    assert ctx["memory_page"] == "Mobility"
    assert "baseline" in ctx
    assert len(ctx["recent_observations"]) > 0

def test_cross_patient_retrieval_rejected(db_session):
    # Attempt retrieving P001 evidence using patient_id=9999
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-021").first()
    assert ev is not None

    with pytest.raises(Exception) as exc:
        MemoryRetriever.retrieve_context_for_evidence(db_session, 9999, ev)
    assert "Patient isolation violation" in str(exc.value)

def test_memory_proposal_generation_and_validation(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-021").first()
    
    ctx = MemoryRetriever.retrieve_context_for_evidence(db_session, p.id, ev)
    proposal_dict = MemoryConsolidator.generate_proposal(ctx)
    assert proposal_dict["memory_page"] == "Mobility"
    assert "EV-CG-021" in proposal_dict["evidence_ids"]

    is_valid, errors = MemoryValidator.validate_proposal(db_session, p.id, ev, proposal_dict)
    assert is_valid is True
    assert len(errors) == 0

def test_malicious_proposal_dementia_rejected(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-003").first()
    
    bad_proposal = {
        "memory_page": "Cognition",
        "category": "cognition",
        "update_type": "NEW_CLAIM",
        "proposed_claim": "Patient has dementia and Alzheimer's disease.",
        "evidence_ids": [ev.evidence_code]
    }
    is_valid, errors = MemoryValidator.validate_proposal(db_session, p.id, ev, bad_proposal)
    assert is_valid is False
    assert any("introduces unconfirmed clinical diagnosis" in e for e in errors)

def test_malicious_proposal_dizziness_etiology_rejected(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-007").first()

    bad_proposal = {
        "memory_page": "Dizziness",
        "category": "dizziness",
        "update_type": "NEW_CLAIM",
        "proposed_claim": "Patient is dizzy likely due to severe dehydration and stroke.",
        "evidence_ids": [ev.evidence_code]
    }
    is_valid, errors = MemoryValidator.validate_proposal(db_session, p.id, ev, bad_proposal)
    assert is_valid is False
    assert any("clinical diagnosis/etiology" in e for e in errors)

def test_near_fall_cannot_become_completed_fall_in_memory(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-031").first()
    assert "almost fell" in ev.original_statement.lower()

    bad_proposal = {
        "memory_page": "Falls",
        "category": "fall",
        "update_type": "NEW_CLAIM",
        "proposed_claim": "Patient fell down onto the bathroom floor.",
        "evidence_ids": [ev.evidence_code]
    }
    is_valid, errors = MemoryValidator.validate_proposal(db_session, p.id, ev, bad_proposal)
    assert is_valid is False
    assert any("Near-fall observation cannot be upgraded into a completed FALL" in e for e in errors)

def test_missing_provenance_rejected(db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-021").first()

    no_prov_proposal = {
        "memory_page": "Mobility",
        "category": "mobility",
        "update_type": "TEMPORAL_UPDATE",
        "proposed_claim": "Patient requires support outside.",
        "evidence_ids": []
    }
    is_valid, errors = MemoryValidator.validate_proposal(db_session, p.id, ev, no_prov_proposal)
    assert is_valid is False
    assert any("PROVENANCE ERROR" in e for e in errors)

def test_consolidate_and_apply_api_pipeline(client, db_session):
    # 1. Consolidate
    res_cons = client.post("/api/memory/consolidate", json={
        "patient_id": "P001",
        "evidence_code": "EV-CG-021"
    })
    assert res_cons.status_code == 201
    prop_data = res_cons.json()
    assert prop_data["status"] == "VALIDATED"
    prop_id = prop_data["proposal_id"]

    # 2. Get Proposal by ID
    res_prop = client.get(f"/api/memory/proposals/{prop_id}")
    assert res_prop.status_code == 200
    assert res_prop.json()["proposal_id"] == prop_id

    # 3. Apply Proposal
    res_apply = client.post(f"/api/memory/apply/{prop_id}")
    assert res_apply.status_code == 200
    apply_data = res_apply.json()
    assert apply_data["status"] == "APPLIED"
    assert apply_data["version"] >= 1
    assert "Mobility" in apply_data["wiki_page"]

    # 4. Cannot re-apply already applied proposal
    res_reapply = client.post(f"/api/memory/apply/{prop_id}")
    assert res_reapply.status_code == 400

import uuid

def test_proposal_state_machine_rejected_cannot_apply(client, db_session):
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-003").first()

    # Create directly a rejected proposal in DB
    rejected_prop = MemoryProposal(
        proposal_code=f"PROP-REJ-{uuid.uuid4().hex[:8]}",
        patient_id=p.id,
        evidence_id=ev.id,
        evidence_code=ev.evidence_code,

        memory_page="Cognition",
        category="cognition",
        update_type="NEW_CLAIM",
        proposed_claim="Patient has dementia.",
        information_state="AI_DERIVED",
        evidence_ids=[ev.evidence_code],
        confidence="LOW",
        status="REJECTED",
        validation_errors=["Clinical diagnosis prohibited."]
    )
    db_session.add(rejected_prop)
    db_session.commit()
    db_session.refresh(rejected_prop)

    # Attempt to apply rejected proposal
    res_apply = client.post(f"/api/memory/apply/{rejected_prop.id}")
    assert res_apply.status_code == 400
    assert "Only 'VALIDATED' proposals can be applied" in res_apply.json()["detail"]
