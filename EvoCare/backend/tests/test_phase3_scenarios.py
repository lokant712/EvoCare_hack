import pytest
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

def test_scenario_weakness_mobility_pipeline(client):
    # Input: "She is weak and holding walls."
    start = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is weak and holding walls."
    }).json()
    assert start["category"] == "mobility"
    assert "support_needed" in start["missing_fields"] or "activity" in start["missing_fields"]
    
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "support_needed",
        "answer": "Held furniture/walls"
    })
    client.post(f"/api/clarification/{start['session_id']}/answer", json={
        "field_name": "activity",
        "answer": "Walking indoors"
    })
    comp = client.post(f"/api/clarification/{start['session_id']}/complete").json()
    assert comp["structured_observation"]["category"] == "mobility"
    assert comp["structured_observation"]["attributes"]["support_needed"] == "Held furniture/walls"

def test_evidence_id_generation_sequential(client):
    start1 = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She ate half her lunch."
    }).json()
    comp1 = client.post(f"/api/clarification/{start1['session_id']}/complete").json()
    
    start2 = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She ate all her dinner."
    }).json()
    comp2 = client.post(f"/api/clarification/{start2['session_id']}/complete").json()

    assert comp1["evidence_code"].startswith("EV-CG-")
    assert comp2["evidence_code"].startswith("EV-CG-")
    assert comp1["evidence_code"] != comp2["evidence_code"]

