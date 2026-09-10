from app.models.patient import Patient

def test_patient_p001_exists(db_session):
    patient = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    assert patient is not None
    assert patient.name == "Meenakshi Raman"
    assert patient.age == 78
    assert patient.sex == "Female"
    assert "Chennai" in patient.location

def test_patient_is_synthetic(db_session):
    patient = db_session.query(Patient).filter(Patient.patient_code == "P001").first()
    assert patient.is_synthetic is True

def test_patient_api_endpoints(client):
    res = client.get("/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) >= 1
    assert patients[0]["patient_code"] == "P001"

    res_single = client.get(f"/api/patients/{patients[0]['id']}")
    assert res_single.status_code == 200
    assert res_single.json()["name"] == "Meenakshi Raman"

    res_summary = client.get(f"/api/patients/{patients[0]['id']}/summary")
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert "baseline" in summary
    assert "current_diagnoses" in summary
    assert len(summary["current_diagnoses"]) == 4
