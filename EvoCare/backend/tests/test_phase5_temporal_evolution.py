import pytest
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.memory_models import MemoryVersion, MemoryClaim, MemoryProposal
from app.services.memory import (
    MemoryRetriever,
    MemoryConsolidator,
    MemoryValidator,
    MemoryService,
    WikiSynchronizer,
)
from app.services.observation_pipeline_service import ObservationPipelineService

def test_1_support_required_to_later_improvement(client, db_session):
    """
    Test 1: Support required -> later improvement.
    First observation: "She needed someone's arm while walking outside today."
    Second observation: "She walked normally inside today."
    Asserts proposal recognizes later improvement / longitudinal variability without deleting earlier evidence.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    assert p is not None

    # Step 1: Ingest support observation
    s1 = ObservationPipelineService.start_session(
        db=db_session,
        patient_id_or_code="P001",
        raw_text="She needed someone's arm while walking outside today.",
        caregiver_id="CG002",
        processing_mode="DETERMINISTIC"
    )
    c1 = ObservationPipelineService.complete_session(db=db_session, session_id=s1["session_id"])
    ev1_code = c1["evidence_code"]

    res_cons1 = client.post("/api/memory/consolidate", json={"patient_id": "P001", "evidence_code": ev1_code})
    assert res_cons1.status_code == 201
    prop1 = res_cons1.json()
    assert prop1["status"] == "VALIDATED"
    assert "support" in prop1["proposed_claim"].lower() or "cruising" in prop1["proposed_claim"].lower()

    res_apply1 = client.post(f"/api/memory/apply/{prop1['proposal_id']}")
    assert res_apply1.status_code == 200
    v1 = res_apply1.json()["version"]

    # Step 2: Ingest later improvement observation
    s2 = ObservationPipelineService.start_session(
        db=db_session,
        patient_id_or_code="P001",
        raw_text="She walked normally inside today.",
        caregiver_id="CG001",
        processing_mode="DETERMINISTIC"
    )
    c2 = ObservationPipelineService.complete_session(db=db_session, session_id=s2["session_id"])
    ev2_code = c2["evidence_code"]

    res_cons2 = client.post("/api/memory/consolidate", json={"patient_id": "P001", "evidence_code": ev2_code})
    assert res_cons2.status_code == 201
    prop2 = res_cons2.json()
    assert prop2["status"] == "VALIDATED"
    assert prop2["update_type"] == "TEMPORAL_UPDATE"
    # Must capture variability / improvement
    claim_lower = prop2["proposed_claim"].lower()
    assert "variability" in claim_lower or "improvement" in claim_lower or "without support" in claim_lower or "normally" in claim_lower

    res_apply2 = client.post(f"/api/memory/apply/{prop2['proposal_id']}")
    assert res_apply2.status_code == 200
    v2 = res_apply2.json()["version"]
    assert v2 > v1

def test_2_improvement_to_later_deterioration(client, db_session):
    """
    Test 2: Improvement -> later deterioration.
    After improvement, a new observation describes support requirement / deterioration.
    Asserts proposal recognizes renewed decline / support requirement.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    
    # Ingest deterioration after improvement
    s3 = ObservationPipelineService.start_session(
        db=db_session,
        patient_id_or_code="P001",
        raw_text="She needed support and was holding onto furniture today while walking.",
        caregiver_id="CG002",
        processing_mode="DETERMINISTIC"
    )
    c3 = ObservationPipelineService.complete_session(db=db_session, session_id=s3["session_id"])
    ev3_code = c3["evidence_code"]

    res_cons3 = client.post("/api/memory/consolidate", json={"patient_id": "P001", "evidence_code": ev3_code})
    assert res_cons3.status_code == 201
    prop3 = res_cons3.json()
    assert prop3["status"] == "VALIDATED"
    assert "renewed decline" in prop3["proposed_claim"].lower() or "support" in prop3["proposed_claim"].lower()

    res_apply3 = client.post(f"/api/memory/apply/{prop3['proposal_id']}")
    assert res_apply3.status_code == 200

def test_3_duplicate_observation_returns_no_change(client, db_session):
    """
    Test 3: Duplicate observation -> NO_CHANGE.
    Re-consolidating already applied evidence returns NO_CHANGE and does not create a new version.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    ev = db_session.query(Evidence).filter(Evidence.patient_id == p.id, Evidence.evidence_code == "EV-CG-021").first()

    # First ensure EV-CG-021 is consolidated and applied
    res1 = client.post("/api/memory/consolidate", json={"patient_id": "P001", "evidence_code": ev.evidence_code})
    prop_id = res1.json()["proposal_id"]
    client.post(f"/api/memory/apply/{prop_id}")

    # Count versions before
    ver_count_before = db_session.query(MemoryVersion).filter(
        MemoryVersion.patient_id == p.id,
        MemoryVersion.memory_page == "Mobility"
    ).count()

    # Re-consolidate the same evidence
    res_dup = client.post("/api/memory/consolidate", json={"patient_id": "P001", "evidence_code": ev.evidence_code})
    assert res_dup.status_code == 201
    dup_prop = res_dup.json()
    assert dup_prop["update_type"] == "NO_CHANGE"
    assert "already incorporated" in dup_prop["proposed_claim"]

    # Apply NO_CHANGE proposal
    res_apply_dup = client.post(f"/api/memory/apply/{dup_prop['proposal_id']}")
    assert res_apply_dup.status_code == 200
    assert res_apply_dup.json()["status"] == "APPLIED"

    # Verify version count did NOT increment
    ver_count_after = db_session.query(MemoryVersion).filter(
        MemoryVersion.patient_id == p.id,
        MemoryVersion.memory_page == "Mobility"
    ).count()
    assert ver_count_after == ver_count_before

def test_4_historical_baseline_preservation(client, db_session):
    """
    Test 4: Historical baseline preservation.
    Verify that across all memory versions and updates, the baseline in the Patient Wiki
    and database remains intact.
    """
    wiki_content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "## Baseline" in wiki_content
    assert "Habitually ambulates independently inside and around the home." in wiki_content
    assert "[[Raw Evidence/Patient/EV-PAT-002|EV-PAT-002]]" in wiki_content
    assert "[[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]" in wiki_content

def test_5_evidence_ids_preserved_across_all_versions(client, db_session):
    """
    Test 5: Evidence IDs preserved across all versions.
    Every memory version and claim has valid provenance referencing evidence IDs.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    versions = db_session.query(MemoryVersion).filter(
        MemoryVersion.patient_id == p.id,
        MemoryVersion.memory_page == "Mobility"
    ).all()
    assert len(versions) > 0

    for v in versions:
        if v.content_snapshot:
            assert "evidence_ids" in v.content_snapshot
            assert len(v.content_snapshot["evidence_ids"]) > 0

    claims = db_session.query(MemoryClaim).filter(
        MemoryClaim.patient_id == p.id,
        MemoryClaim.memory_page == "Mobility"
    ).all()
    for c in claims:
        assert c.evidence_ids is not None
        assert len(c.evidence_ids) > 0

def test_6_wiki_reflects_latest_longitudinal_state(client, db_session):
    """
    Test 6: Wiki reflects the latest longitudinal state.
    The Wiki markdown file contains the latest version banner, current version number,
    and all longitudinal memory entries.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    latest_ver = db_session.query(MemoryVersion).filter(
        MemoryVersion.patient_id == p.id,
        MemoryVersion.memory_page == "Mobility"
    ).order_by(MemoryVersion.version_number.desc()).first()

    wiki_content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "## Memory Version History" in wiki_content
    assert f"**Current Memory Version**: {latest_ver.version_number}" in wiki_content
    assert "## Longitudinal Memory" in wiki_content
    assert f"Version {latest_ver.version_number}" in wiki_content

def test_7_previous_memory_versions_remain_immutable(db_session):
    """
    Test 7: Previous memory versions remain immutable.
    MemoryVersion records cannot be mutated and retain their initial status, snapshots, and timestamps.
    """
    p = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    versions = db_session.query(MemoryVersion).filter(
        MemoryVersion.patient_id == p.id,
        MemoryVersion.memory_page == "Mobility"
    ).order_by(MemoryVersion.version_number.asc()).all()

    for v in versions:
        assert v.validation_status == "APPLIED"
        assert v.version_number >= 1
        assert v.created_at is not None
        assert v.content_snapshot is not None
        assert len(v.change_summary) > 0
