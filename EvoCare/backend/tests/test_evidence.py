from app.models.evidence import Evidence
from app.models.enums import SourceType, EvidenceStatus

def test_evidence_count_and_immutability(db_session):
    evidences = db_session.query(Evidence).all()
    assert len(evidences) >= 65
    for ev in evidences:
        assert ev.status == EvidenceStatus.IMMUTABLE
        assert ev.evidence_code.startswith("EV-")

def test_evidence_ids_unchanged(db_session):
    expected_codes = ["EV-CG-001", "EV-CG-031", "EV-DR-001", "EV-LAB-001", "EV-MED-001", "EV-PAT-001", "EV-MR-001"]
    for code in expected_codes:
        ev = db_session.query(Evidence).filter(Evidence.evidence_code == code).first()
        assert ev is not None, f"Evidence code {code} missing in database"

def test_evidence_no_update_or_delete_api(client, db_session):
    ev = db_session.query(Evidence).first()
    # Check PUT /api/evidence/{id} returns 405 Method Not Allowed
    put_res = client.put(f"/api/evidence/{ev.evidence_code}", json={"statement": "tampered"})
    assert put_res.status_code == 405

    # Check DELETE /api/evidence/{id} returns 405 Method Not Allowed
    del_res = client.delete(f"/api/evidence/{ev.evidence_code}")
    assert del_res.status_code == 405

def test_evidence_query_filters(client, db_session):
    patient = db_session.query(Evidence).first().patient_id
    res = client.get(f"/api/patients/{patient}/evidence?source_type=CAREGIVER")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 47
    for item in data:
        assert item["source_type"] == "CAREGIVER"
