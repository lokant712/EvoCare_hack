from app.models.medication import Medication
from app.models.enums import SourceType

def test_exact_four_medications_imported(db_session):
    meds = db_session.query(Medication).all()
    assert len(meds) >= 4
    names = [m.name for m in meds]
    assert "Metformin" in names
    assert "Amlodipine" in names
    assert "Atorvastatin" in names
    assert "Paracetamol" in names

    for m in meds:
        if m.name in ["Metformin", "Amlodipine", "Atorvastatin", "Paracetamol"] and m.evidence:
            assert m.evidence.source_type == SourceType.MEDICATION_RECORD
        assert m.status in ("ACTIVE", "PRN (as needed)")

def test_medications_api(client, db_session):
    patient_id = db_session.query(Medication).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/medications")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 4
    names = [m["name"] for m in data]
    assert "Metformin" in names
    assert "Amlodipine" in names
    assert "Atorvastatin" in names
