import pytest
from app.services.clarification_engine import ClarificationEngine
from app.models.clarification import SessionStatus, ClarificationSession
from app.models.evidence import Evidence
from app.models.caregiver_observation import CaregiverObservation

def test_clarification_engine_category_detection():
    assert ClarificationEngine.detect_category("She is dizzy.") == "dizziness"
    assert ClarificationEngine.detect_category("She almost fell near the bathroom.") == "near_fall"
    assert ClarificationEngine.detect_category("She fell down on the floor.") == "fall"
    assert ClarificationEngine.detect_category("She didn't eat much for dinner.") == "nutrition"
    assert ClarificationEngine.detect_category("She seems confused today.") == "cognition"
    assert ClarificationEngine.detect_category("Her knees hurt a lot.") == "pain"
    assert ClarificationEngine.detect_category("She was holding the table while walking.") == "mobility"
    assert ClarificationEngine.detect_category("She slept poorly and woke up 3 times.") == "sleep"
    assert ClarificationEngine.detect_category("She took her morning medicines.") == "medication_adherence"

def test_clarification_engine_missing_fields():
    # Dizziness without severity or onset
    initial = ClarificationEngine.extract_initial_fields("dizziness", "She is dizzy.")
    missing = ClarificationEngine.get_missing_fields("dizziness", initial)
    assert "severity" in missing
    assert "duration" in missing
    assert "onset" in missing

    # Dizziness with extracted onset
    initial_with_onset = ClarificationEngine.extract_initial_fields("dizziness", "She was mildly dizzy after getting out of bed.")
    assert initial_with_onset.get("severity") == "Mild"
    assert "getting out of bed" in initial_with_onset.get("onset", "").lower()

def test_clarification_engine_questions_generation():
    questions = ClarificationEngine.generate_questions("dizziness", ["severity", "duration"])
    assert len(questions) == 2
    field_names = [q["field_name"] for q in questions]
    assert "severity" in field_names
    assert "duration" in field_names
    for q in questions:
        assert len(q["options"]) >= 2

def test_observation_start_api(client):
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy.",
        "caregiver_id": "CG001"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "dizziness"
    assert "session_id" in data
    assert len(data["missing_fields"]) >= 2
    assert len(data["questions"]) >= 2
    assert data["status"] == "PENDING"

def test_get_clarification_session_api(client):
    # Start session
    res_start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy."
    })
    session_id = res_start.json()["session_id"]

    res_get = client.get(f"/api/clarification/{session_id}")
    assert res_get.status_code == 200
    sess_data = res_get.json()
    assert sess_data["id"] == session_id
    assert sess_data["detected_category"] == "dizziness"
    assert len(sess_data["questions"]) >= 2
    assert len(sess_data["answers"]) == 0

def test_submit_clarification_answers(client):
    # Start session
    res_start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy."
    })
    session_id = res_start.json()["session_id"]
    questions = res_start.json()["questions"]

    # Submit answer for question 1 (severity)
    q1 = questions[0]
    res_ans1 = client.post(f"/api/clarification/{session_id}/answer", json={
        "question_id": q1["id"],
        "answer": "Moderate"
    })
    assert res_ans1.status_code == 200
    assert res_ans1.json()["field_name"] == q1["field_name"]
    assert res_ans1.json()["answer"] == "Moderate"

    # Submit answer by field_name (duration)
    res_ans2 = client.post(f"/api/clarification/{session_id}/answer", json={
        "field_name": "duration",
        "answer": "5 minutes"
    })
    assert res_ans2.status_code == 200
    assert res_ans2.json()["answer"] == "5 minutes"

def test_complete_clarification_session(client, db_session):
    # Start session
    res_start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy.",
        "caregiver_id": "CG002"
    })
    session_id = res_start.json()["session_id"]

    # Answer questions
    client.post(f"/api/clarification/{session_id}/answer", json={
        "field_name": "severity",
        "answer": "Moderate"
    })
    client.post(f"/api/clarification/{session_id}/answer", json={
        "field_name": "duration",
        "answer": "5 minutes"
    })
    client.post(f"/api/clarification/{session_id}/answer", json={
        "field_name": "onset",
        "answer": "After standing"
    })

    # Complete
    res_comp = client.post(f"/api/clarification/{session_id}/complete")
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["status"] == "COMPLETED"
    assert comp_data["category"] == "dizziness"
    assert "evidence_code" in comp_data
    assert comp_data["evidence_code"].startswith("EV-CG-")

    # Verify structured observation
    struct = comp_data["structured_observation"]
    assert struct["category"] == "dizziness"
    assert struct["attributes"]["severity"] == "Moderate"
    assert struct["attributes"]["duration"] == "5 minutes"
    assert struct["attributes"]["onset"] == "After standing"
    assert struct["clarification_complete"] is True
    assert struct["clinical_diagnoses_inferred"] is False

    # Verify Evidence exists in DB
    ev = db_session.query(Evidence).filter(Evidence.evidence_code == comp_data["evidence_code"]).first()
    assert ev is not None
    assert ev.original_statement == "She is dizzy."
    assert ev.source_id == "CG002"

def test_safety_rule_no_stroke_or_etiology_inferred(client):
    # Dizziness should never infer stroke or vestibular pathology
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She was severely dizzy this morning."
    }).json()
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    struct = comp["structured_observation"]
    assert "stroke" not in str(struct).lower()
    assert "vertigo diagnosis" not in str(struct).lower()
    assert struct["clinical_diagnoses_inferred"] is False

def test_safety_rule_no_dementia_diagnosis_on_confusion(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She forgot what day it was and seemed confused."
    }).json()
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    struct = comp["structured_observation"]
    assert struct.get("dementia_diagnosed") is False
    assert "alzheimer" not in str(struct).lower()
    assert "dementia" not in str(struct.get("attributes", {})).lower() or struct["attributes"].get("diagnosis") is None

def test_behavior_category_pipeline(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She seemed agitated and restless during the evening."
    }).json()
    assert start["category"] == "behavior"
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "mood_description",
        "answer": "Agitated / Restless"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["category"] == "behavior"
    assert comp["structured_observation"]["attributes"]["mood_description"] == "Agitated / Restless"

def test_fall_vs_near_fall_strict_separation(client):
    start_fall = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She fell down onto the kitchen floor."
    }).json()
    assert start_fall["category"] == "fall"

    start_near = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She lost balance and almost fell but grabbed the counter."
    }).json()
    assert start_near["category"] == "near_fall"

def test_options_provided_for_all_categories():
    categories = ["mobility", "fall", "near_fall", "dizziness", "nutrition", "cognition", "sleep", "pain", "behavior", "medication_adherence"]
    for cat in categories:
        missing = ClarificationEngine.get_missing_fields(cat, {})
        questions = ClarificationEngine.generate_questions(cat, missing)
        assert len(questions) > 0, f"Category {cat} should have questions"
        for q in questions:
            assert len(q["options"]) >= 2, f"Question {q['field_name']} in {cat} must have at least 2 options"
            assert isinstance(q["question"], str) and len(q["question"]) > 5


