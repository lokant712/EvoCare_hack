from app.models.doctor_record import DoctorRecord
from app.models.enums import SourceType

def test_doctor_records_imported(db_session):
    drs = db_session.query(DoctorRecord).all()
    assert len(drs) >= 5
    for dr in drs:
        assert dr.evidence.source_type == SourceType.DOCTOR
        assert dr.doctor_id is not None



def test_clinical_and_caregiver_separation(client, db_session):
    patient_id = db_session.query(DoctorRecord).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/clinical")
    assert res.status_code == 200
    clinical_data = res.json()
    
    # Verify clinical endpoint contains ONLY clinician & lab data
    assert "diagnoses" in clinical_data
    assert "doctor_records" in clinical_data
    assert "labs" in clinical_data
    assert "medications" in clinical_data
    assert len(clinical_data["doctor_records"]) >= 5
    
    # Ensure no caregiver observations are present in clinical records
    for dr in clinical_data["doctor_records"]:
        assert "CG00" not in dr["doctor_id"]
