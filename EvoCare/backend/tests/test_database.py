from app.models.patient import Patient
from app.models.evidence import Evidence

def test_database_initialization(db_session):
    assert db_session is not None
    patients = db_session.query(Patient).all()
    assert len(patients) >= 1

def test_evidence_table_populated(db_session):
    ev_count = db_session.query(Evidence).count()
    assert ev_count >= 65
