from app.models.conflict import Conflict

def test_three_conflicts_imported(db_session):
    conflicts = db_session.query(Conflict).all()
    assert len(conflicts) == 3
    cats = [c.category for c in conflicts]
    assert "mobility" in cats
    assert "falls" in cats
    assert "nutrition" in cats

def test_conflicts_do_not_auto_resolve(db_session):
    for c in db_session.query(Conflict).all():
        assert c.status in ("CONFLICTING", "REQUIRES_CLINICIAN_REVIEW")
        assert c.resolved_at is None
        assert len(c.supporting_evidences) >= 2

def test_conflicts_api(client, db_session):
    patient_id = db_session.query(Conflict).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/conflicts")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 3
