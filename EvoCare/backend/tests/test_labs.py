from app.models.lab import LabRecord
from app.models.enums import SourceType

def test_labs_imported_with_exact_values(db_session):
    labs = db_session.query(LabRecord).all()
    assert len(labs) == 15  # 3 panels x 5 tests
    for l in labs:
        assert l.evidence.source_type == SourceType.LAB_RECORD
        assert l.test_name in ("HbA1c", "Serum Creatinine", "Serum Sodium", "Serum Potassium", "Hemoglobin")

    # Check HbA1c progression
    hba1c_vals = [l.value for l in db_session.query(LabRecord).filter(LabRecord.test_name == "HbA1c").order_by(LabRecord.observed_at).all()]
    assert hba1c_vals == ["7.1", "7.3", "7.4"]

def test_labs_api(client, db_session):
    patient_id = db_session.query(LabRecord).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/labs")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 15
