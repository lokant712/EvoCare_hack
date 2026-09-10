from app.models.caregiver_observation import CaregiverObservation
from app.models.enums import SourceType

def test_caregiver_observations_imported(db_session):
    cg_obs = db_session.query(CaregiverObservation).all()
    assert len(cg_obs) >= 47
    for obs in cg_obs:
        assert obs.evidence.source_type == SourceType.CAREGIVER
        assert obs.caregiver_id is not None


def test_near_fall_classification_preserved(db_session):
    # EV-CG-031 must be classified as NEAR_FALL and not a completed fall
    near_fall = db_session.query(CaregiverObservation).filter(
        CaregiverObservation.observation_text.like("%almost fell%")
    ).first()
    assert near_fall is not None
    assert near_fall.attributes.get("classification") == "NEAR_FALL"
    assert near_fall.attributes.get("ground_impact") is False

def test_caregiver_api_endpoint(client, db_session):
    patient_id = db_session.query(CaregiverObservation).first().patient_id
    res = client.get(f"/api/patients/{patient_id}/caregiver-observations?category=mobility")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 5
    for item in data:
        assert item["source_type"] == "CAREGIVER"
        assert item["category"] == "mobility"
