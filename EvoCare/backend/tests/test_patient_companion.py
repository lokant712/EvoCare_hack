import pytest
from fastapi.testclient import TestClient
from app.core.database import SessionLocal
from app.models.security import User
from app.models.audit import AuditLog
from app.core.security import create_access_token


def test_unauthenticated_patient_companion_rejected(client):
    c = TestClient(client.app)
    res = c.post("/api/patients/P001/companion", json={"question": "When should I take my medicines?"})
    assert res.status_code == 401


def test_patient_self_access_companion_allowed(client):
    db = SessionLocal()
    patient_user = db.query(User).filter(User.username == "patient.demo").first()
    assert patient_user is not None
    token = create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username, "role": "PATIENT"})
    db.close()

    c = TestClient(client.app)
    c.headers.update({"Authorization": f"Bearer {token}"})

    res = c.post("/api/patients/P001/companion", json={"question": "What medicines am I taking?"})
    assert res.status_code == 200
    data = res.json()
    assert data["patient_code"] == "P001"
    assert "Metformin" in data["answer"] or "medicine" in data["answer"].lower() or "health" in data["answer"].lower()
    assert "disclaimer" in data


def test_patient_cross_patient_companion_forbidden(client):
    db = SessionLocal()
    patient_user = db.query(User).filter(User.username == "patient.demo").first()
    token = create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username, "role": "PATIENT"})
    db.close()

    c = TestClient(client.app)
    c.headers.update({"Authorization": f"Bearer {token}"})

    # Patient only has grant for P001, querying P002 must be 403 Forbidden
    res = c.post("/api/patients/P002/companion", json={"question": "What are the doctor notes?"})
    assert res.status_code == 403


def test_patient_cannot_access_doctor_clinical_reasoning(client):
    db = SessionLocal()
    patient_user = db.query(User).filter(User.username == "patient.demo").first()
    token = create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username, "role": "PATIENT"})
    db.close()

    c = TestClient(client.app)
    c.headers.update({"Authorization": f"Bearer {token}"})

    # Clinical reasoning is doctor-only
    res = c.post("/api/clinical-reasoning/P001", json={"question": "Differential diagnosis"})
    assert res.status_code == 403


def test_patient_companion_audit_logged(client):
    db = SessionLocal()
    initial_count = db.query(AuditLog).filter(AuditLog.action == "PATIENT_COMPANION_QUERY").count()
    patient_user = db.query(User).filter(User.username == "patient.demo").first()
    token = create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username, "role": "PATIENT"})
    db.close()

    c = TestClient(client.app)
    c.headers.update({"Authorization": f"Bearer {token}"})

    res = c.post("/api/patients/P001/companion", json={"question": "When is my next checkup?"})
    assert res.status_code == 200

    db = SessionLocal()
    new_count = db.query(AuditLog).filter(AuditLog.action == "PATIENT_COMPANION_QUERY").count()
    db.close()
    assert new_count > initial_count


def test_patient_companion_guardrail_triggered(client):
    db = SessionLocal()
    patient_user = db.query(User).filter(User.username == "patient.demo").first()
    token = create_access_token(data={"sub": str(patient_user.id), "username": patient_user.username, "role": "PATIENT"})
    db.close()

    c = TestClient(client.app)
    c.headers.update({"Authorization": f"Bearer {token}"})

    # Out of scope / chit-chat question
    res = c.post("/api/patients/P001/companion", json={"question": "how are you?"})
    assert res.status_code == 200
    data = res.json()
    assert "EvoCare Personal Health Companion" in data["answer"]
    assert "medical records" in data["answer"].lower() or "health records" in data["answer"].lower()

