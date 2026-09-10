from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.caregiver_observation import CaregiverObservation

def test_baseline_preservation(db_session):
    baselines = db_session.query(Baseline).all()
    assert len(baselines) >= 8
    mobility_b = db_session.query(Baseline).filter(Baseline.category == "mobility").first()
    assert "Independently Mobile" in mobility_b.baseline_value

def test_mobility_improvement_recorded(db_session):
    # 2026-09-09 observation must be present
    obs_0909 = db_session.query(CaregiverObservation).filter(
        CaregiverObservation.observation_text.like("%walking better today%")
    ).first()
    assert obs_0909 is not None
    assert obs_0909.attributes.get("improvement") is True

def test_timeline_is_chronological(client, db_session):
    patient_id = db_session.query(Baseline).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/timeline")
    assert res.status_code == 200
    timeline = res.json()
    assert len(timeline) >= 50
    
    dates = [t["observed_at"] for t in timeline]
    assert dates == sorted(dates), "Timeline events must be in strict chronological order"

def test_memory_endpoint(client, db_session):
    patient_id = db_session.query(Baseline).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/memory")
    assert res.status_code == 200
    mem = res.json()
    assert "executive_summary" in mem
    assert len(mem["baseline"]) >= 8
    assert len(mem["active_patterns"]) >= 6
    assert len(mem["unresolved_conflicts"]) >= 3
    assert len(mem["recent_improvements"]) >= 4
    assert len(mem["unknown_information"]) >= 5
