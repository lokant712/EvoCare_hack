import pytest
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.caregiver_observation import CaregiverObservation
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.services.dashboard_service import DashboardService

def test_dashboard_endpoint_p001(client, db_session):
    """
    Test 1: Dashboard endpoint returns complete aggregated response for P001.
    """
    res = client.get("/api/dashboard/patients/P001")
    assert res.status_code == 200
    data = res.json()
    assert "patient" in data
    assert "overview" in data
    assert "recent_changes" in data
    assert "clinical_diagnoses" in data
    assert "medications" in data
    assert "labs" in data
    assert "caregiver_observations" in data
    assert "longitudinal_memory" in data
    assert "timeline" in data
    assert "conflicts" in data
    assert "fall_safety" in data
    assert "provenance_map" in data

def test_patient_demographics_and_synthetic_badge(client):
    """
    Test 2: Patient demographics are accurate and labeled as SYNTHETIC DEMO DATA.
    """
    res = client.get("/api/dashboard/patients/P001")
    assert res.status_code == 200
    p = res.json()["patient"]
    assert p["patient_code"] == "P001"
    assert p["name"] == "Meenakshi Raman"
    assert p["age"] == 78
    assert p["sex"] == "Female"
    assert p["dataset_type"] == "SYNTHETIC DEMO DATA"

def test_clinical_data_diagnoses_and_medications(client):
    """
    Test 3: Clinician-confirmed diagnoses and active medications are present.
    """
    res = client.get("/api/dashboard/patients/P001")
    data = res.json()
    
    # Diagnoses
    diagnoses = data["clinical_diagnoses"]
    assert len(diagnoses) >= 4
    diag_descs = [d["description"].lower() for d in diagnoses]
    assert any("type 2 diabetes" in d for d in diag_descs)
    assert any("hypertension" in d for d in diag_descs)
    assert any("osteoarthritis" in d for d in diag_descs)
    
    # Medications
    meds = data["medications"]
    assert len(meds) >= 4
    med_names = [m["name"].lower() for m in meds]
    assert any("metformin" in m for m in med_names)
    assert any("amlodipine" in m for m in med_names)
    assert any("atorvastatin" in m for m in med_names)

def test_laboratory_timeline_without_speculative_diagnosis(client):
    """
    Test 4: Laboratory results timeline renders historical values and dates without inferred diagnoses.
    """
    res = client.get("/api/dashboard/patients/P001")
    labs = res.json()["labs"]
    assert len(labs) >= 1
    for l in labs:
        assert "test_name" in l
        assert "value" in l
        assert "date" in l
        assert "evidence_code" in l

def test_caregiver_observations_separation(client):
    """
    Test 5: Caregiver observations are kept strictly separated from doctor records.
    """
    res = client.get("/api/dashboard/patients/P001")
    cg_obs = res.json()["caregiver_observations"]
    assert len(cg_obs) > 0
    for obs in cg_obs:
        assert "caregiver_id" in obs
        assert "observation_text" in obs
        assert "evidence_code" in obs
        assert obs["evidence_code"].startswith("EV-CG")

def test_longitudinal_memory_and_version_tracking(client):
    """
    Test 6: Longitudinal memory returns baseline, recent changes, version number, and claims.
    """
    res = client.get("/api/dashboard/patients/P001")
    mem = res.json()["longitudinal_memory"]
    assert mem["current_version"] >= 1
    assert "baseline" in mem
    assert "recent_changes" in mem
    assert "unknowns" in mem
    assert "active_claims" in mem

def test_patient_timeline_chronology_and_badges(client):
    """
    Test 7: Patient timeline contains events from multiple sources with distinct badges.
    """
    res = client.get("/api/dashboard/patients/P001")
    timeline = res.json()["timeline"]
    assert len(timeline) >= 5
    badges = {evt["badge"] for evt in timeline}
    assert "CLINICIAN-CONFIRMED" in badges
    assert "CAREGIVER-REPORTED" in badges
    assert "LAB" in badges

def test_conflict_dual_perspective_preservation(client):
    """
    Test 8: Conflicts preserve doctor vs caregiver views without premature resolution.
    """
    res = client.get("/api/dashboard/patients/P001")
    conflicts = res.json()["conflicts"]
    assert len(conflicts) > 0
    c = conflicts[0]
    assert "doctor_view" in c
    assert "caregiver_view" in c
    assert "context" in c
    assert c["status"] in ("CONTEXTUAL", "UNRESOLVED", "RESOLVED", "CONFLICTING")

def test_provenance_and_why_map(client):
    """
    Test 9: Provenance map contains exact original statements, timestamps, and linked claims.
    """
    res = client.get("/api/dashboard/patients/P001")
    prov_map = res.json()["provenance_map"]
    assert "EV-PAT-002" in prov_map
    assert "EV-DR-001" in prov_map
    assert "EV-CG-021" in prov_map
    
    ev21 = prov_map["EV-CG-021"]
    assert ev21["source_type"] == "CAREGIVER"
    assert len(ev21["original_statement"]) > 10

def test_fall_safety_near_fall_invariant(client):
    """
    Test 10: Near-fall event is never classified as a completed fall.
    """
    res = client.get("/api/dashboard/patients/P001")
    fall_safety = res.json()["fall_safety"]
    assert fall_safety["completed_falls_count"] == 0
    assert fall_safety["near_falls_count"] == 1
    assert len(fall_safety["near_fall_events"]) == 1
    assert fall_safety["near_fall_events"][0]["ground_impact"] is False

def test_cross_patient_isolation(client):
    """
    Test 11: Attempting to query a non-existent patient returns 404 and does not leak data.
    """
    res = client.get("/api/dashboard/patients/P9999_NON_EXISTENT")
    assert res.status_code == 404

def test_dashboard_is_read_only(client, db_session):
    """
    Test 12: Calling dashboard API does not mutate any database records.
    """
    ev_count_before = db_session.query(Evidence).count()
    cg_count_before = db_session.query(CaregiverObservation).count()
    
    res = client.get("/api/dashboard/patients/P001")
    assert res.status_code == 200

    ev_count_after = db_session.query(Evidence).count()
    cg_count_after = db_session.query(CaregiverObservation).count()

    assert ev_count_after == ev_count_before
    assert cg_count_after == cg_count_before
