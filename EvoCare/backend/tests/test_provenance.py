from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.observation import Observation

def test_pattern_provenance(client, db_session):
    pattern = db_session.query(Pattern).first()
    assert pattern is not None
    res = client.get(f"/api/patterns/{pattern.id}/evidence")
    assert res.status_code == 200
    prov = res.json()
    assert prov["pattern_id"] == pattern.id
    assert len(prov["supporting_evidence"]) >= 1
    for ev in prov["supporting_evidence"]:
        assert "evidence_code" in ev
        assert "source_type" in ev

def test_conflict_provenance(client, db_session):
    conflict = db_session.query(Conflict).first()
    assert conflict is not None
    res = client.get(f"/api/conflicts/{conflict.id}/evidence")
    assert res.status_code == 200
    prov = res.json()
    assert prov["conflict_id"] == conflict.id
    assert len(prov["supporting_evidence"]) >= 1

def test_observation_provenance(client, db_session):
    obs = db_session.query(Observation).first()
    assert obs is not None
    res = client.get(f"/api/observations/{obs.id}/evidence")
    assert res.status_code == 200
    ev = res.json()
    assert ev["evidence_code"] == obs.evidence.evidence_code
