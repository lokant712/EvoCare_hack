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


def test_doctor_clinical_entry_and_markdown_generation(client, db_session):
    from app.models.patient import Patient
    p001 = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    assert p001 is not None

    payload = {
        "consultation_title": "Geriatric Follow-up & Balance Assessment",
        "clinical_notes": "Patient reported dizziness upon standing in the morning. Blood pressure orthostatics advised.",
        "diagnoses": [
            {
                "condition": "Orthostatic Hypotension",
                "icd_code": "I95.1",
                "status": "CONFIRMED",
                "notes": "Correlates with caregiver-observed morning instability."
            }
        ],
        "prescriptions": [
            {
                "medication_name": "Meclizine",
                "dose": "25 mg",
                "frequency": "Once daily as needed",
                "indication": "Vestibular / positional dizziness",
                "instructions": "Take with breakfast."
            }
        ]
    }

    res = client.post(f"/api/patients/{p001.patient_code}/entries", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert data["diagnoses_recorded"] == 1
    assert data["prescriptions_recorded"] == 1
    assert len(data["evidence_codes_generated"]) == 2
    assert "Orthostatic Hypotension" in data["markdown_content"]
    assert "Meclizine" in data["markdown_content"]
    assert "| **Orthostatic Hypotension** | `I95.1` |" in data["markdown_content"]

    # Verify retrieval endpoint
    get_res = client.get(f"/api/patients/{p001.patient_code}/entries")
    assert get_res.status_code == 200
    entries = get_res.json()
    assert len(entries["diagnoses"]) >= 1
    assert len(entries["medications"]) >= 1

    # Clean up test entries so subsequent medication tests preserve exact baseline counts
    from app.models.medication import Medication
    from app.models.evidence import Evidence
    db_session.query(Medication).filter(Medication.name == "Meclizine").delete()
    db_session.query(DoctorRecord).filter(DoctorRecord.content.contains("Orthostatic Hypotension")).delete()
    for ev_id in data["evidence_codes_generated"]:
        db_session.query(Evidence).filter(Evidence.evidence_code == ev_id).delete()
    db_session.commit()
