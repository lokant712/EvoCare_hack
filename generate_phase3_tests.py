import os

ROOT_DIR = r"c:\Users\lokan\Downloads\journey\sve\EvoCare"
TESTS_DIR = os.path.join(ROOT_DIR, "backend", "tests")

def write_test(rel_path, content):
    full_path = os.path.join(TESTS_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created test: backend/tests/{rel_path}")

# test_phase3_clarification.py
write_test("test_phase3_clarification.py", """import pytest
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
""")

# test_phase3_scenarios.py
write_test("test_phase3_scenarios.py", """import pytest
from app.models.evidence import Evidence
from app.models.caregiver_observation import CaregiverObservation

def test_scenario_1_dizziness_pipeline(client):
    # Input: "She is dizzy."
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy."
    }).json()
    assert start["category"] == "dizziness"
    assert "severity" in start["missing_fields"]
    assert "duration" in start["missing_fields"]

    # Answer
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "severity",
        "answer": "Mild"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "duration",
        "answer": "A few seconds"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "onset",
        "answer": "After getting out of bed / standing up"
    })

    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["severity"] == "Mild"
    assert comp["structured_observation"]["etiology"] == "UNKNOWN (Requires Clinician Evaluation)"

def test_scenario_2_near_fall_pipeline(client, db_session):
    # Input: "She almost fell near the kitchen."
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She almost fell near the kitchen."
    }).json()
    assert start["category"] == "near_fall"
    
    # Answer location & assistance
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "location",
        "answer": "Living room / Kitchen"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "injury",
        "answer": "No injury (caught before impact)"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "assistance_required",
        "answer": "Yes, caught by caregiver"
    })

    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["classification"] == "NEAR_FALL"
    assert comp["structured_observation"]["ground_impact"] is False

def test_scenario_3_nutrition_pipeline(client):
    # Input: "She didn't eat much."
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She didn't eat much."
    }).json()
    assert start["category"] == "nutrition"
    assert "meal" in start["missing_fields"]

    # Answer
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "meal",
        "answer": "Dinner"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "amount_eaten",
        "answer": "Only a few bites (<25%)"
    })

    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["meal"] == "Dinner"
    assert comp["structured_observation"]["attributes"]["amount_eaten"] == "Only a few bites (<25%)"

def test_scenario_4_cognition_pipeline(client):
    # Input: "She seems confused."
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She seems confused."
    }).json()
    assert start["category"] == "cognition"

    # Answer
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "description",
        "answer": "Disoriented to time/day"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "duration",
        "answer": "Brief moment (few minutes)"
    })

    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["dementia_diagnosed"] is False
    assert comp["structured_observation"]["attributes"]["description"] == "Disoriented to time/day"

def test_pain_pipeline(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "Her knees hurt."
    }).json()
    assert start["category"] == "pain"
    
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "location",
        "answer": "Bilateral knees"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "severity",
        "answer": "Mild"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["location"] == "Bilateral knees"

def test_mobility_pipeline(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She was holding the dining table."
    }).json()
    assert start["category"] == "mobility"

    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "support_needed",
        "answer": "Held furniture/walls"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "activity",
        "answer": "Walking indoors"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["support_needed"] == "Held furniture/walls"

def test_sleep_pipeline(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She woke up in the night."
    }).json()
    assert start["category"] == "sleep"

    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "hours_slept",
        "answer": "Around 7-8 hours (normal)"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "night_waking",
        "answer": "Woke up 1-2 times"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["hours_slept"] == "Around 7-8 hours (normal)"

def test_unknown_fields_preserved_when_unanswered(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She had knee pain."
    }).json()

    # Complete without answering all optional questions
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["attributes"]["location"] in ("Bilateral knees", "UNKNOWN")
    assert comp["structured_observation"]["attributes"]["severity"] == "UNKNOWN"

def test_timeline_updates_after_observation_ingested(client):
    # Count initial timeline
    t_before = client.get("/api/patients/1/timeline").json()

    # Ingest new observation
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She walked across the garden today with help."
    }).json()
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "support_needed",
        "answer": "Needed caregiver arm support"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "activity",
        "answer": "Walking outdoors"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()

    # Count timeline after
    t_after = client.get("/api/patients/1/timeline").json()
    assert len(t_after) == len(t_before) + 1
    latest_event = t_after[-1]
    assert latest_event["evidence_code"] == comp["evidence_code"]

def test_get_observation_by_id_endpoint(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She took her evening medicines."
    }).json()
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "taken_on_time",
        "answer": "Taken on time"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "assistance_provided",
        "answer": "Taken independently"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    obs_id = comp["observation_id"]

    res_get = client.get(f"/api/observations/{obs_id}")
    assert res_get.status_code == 200
    data = res_get.json()
    assert data["id"] == obs_id
    assert data["category"] == "medication_adherence"
    assert data["clarification_completed"] is True

def test_session_not_found_error(client):
    res = client.get("/api/clarification/999999")
    assert res.status_code == 404

def test_cannot_answer_completed_session(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is in a good mood."
    }).json()
    client.post(f"/api/clarification/{start['session_id']}/complete")
    
    # Try answering after completion
    res = client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "mood_description",
        "answer": "Cheerful / Social"
    })
    assert res.status_code == 400

def test_cannot_complete_already_completed_session(client):
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She was quiet in the room."
    }).json()
    client.post(f"/api/clarification/{start['session_id']}/complete")
    
    # Try completing again
    res = client.post(f"/api/clarification/{start['session_id']}/complete")
    assert res.status_code == 400

def test_patient_not_found_on_start(client):
    res = client.post("/api/observations/start", json={
        "patient_code": "NON_EXISTENT_PATIENT",
        "text": "She is dizzy."
    })
    assert res.status_code == 404
""")

print("Phase 3 tests generated.")
