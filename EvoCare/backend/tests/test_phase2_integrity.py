from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.observation import Observation
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord

def test_no_cross_patient_relationships(db_session):
    for ev in db_session.query(Evidence).all():
        assert ev.patient_id is not None
    for obs in db_session.query(Observation).all():
        assert obs.patient_id == obs.evidence.patient_id
    for p in db_session.query(Pattern).all():
        for ev in p.supporting_evidences:
            assert ev.patient_id == p.patient_id
    for c in db_session.query(Conflict).all():
        for ev in c.supporting_evidences:
            assert ev.patient_id == c.patient_id


def test_safety_rule_no_unconfirmed_dementia_diagnosis(db_session):
    for p in db_session.query(Pattern).all():
        assert "patient has dementia" not in p.title.lower()
        assert "diagnosed with dementia" not in p.description.lower()
    for dr in db_session.query(DoctorRecord).all():
        assert "dementia" not in dr.content.lower()

def test_safety_rule_no_hallucinated_dizziness_cause(db_session):
    diz_pattern = db_session.query(Pattern).filter(Pattern.category == "dizziness").first()
    assert diz_pattern is not None
    assert "cause unknown" in diz_pattern.description.lower() or "underlying etiology" in diz_pattern.description.lower()

def test_ambiguity_cases_remain_unknown(db_session):
    ambig_cases = ["EV-CG-043", "EV-CG-044", "EV-CG-045", "EV-CG-046", "EV-CG-047"]
    for code in ambig_cases:
        cg = db_session.query(CaregiverObservation).join(Evidence).filter(Evidence.evidence_code == code).first()
        assert cg is not None
        assert cg.attributes.get("clarification_required") is True
        assert len(cg.attributes.get("missing_fields", [])) >= 1
