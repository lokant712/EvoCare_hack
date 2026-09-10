import pytest
from app.services.llm import (
    ParsedCaregiverObservation,
    ObservationCategory,
    EventType,
    CertaintyState,
    ConfidenceLevel,
    MockLLMProvider,
)
from app.services.observation_pipeline_service import ObservationPipelineService

@pytest.fixture(autouse=True)
def setup_mock_llm():
    mock = MockLLMProvider()
    ObservationPipelineService.set_llm_provider(mock)
    yield
    ObservationPipelineService.set_llm_provider(None)

def test_scenario_a_simple_dizziness(client):
    # Scenario A: "She is dizzy."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is dizzy.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "dizziness"
    assert "severity" in data["missing_fields"]
    assert "duration" in data["missing_fields"]
    assert "onset" in data["missing_fields"]
    assert data["observation"]["requires_clarification"] is True

def test_scenario_b_dizziness_with_details_no_redundancy(client):
    # Scenario B: "She had severe dizziness for about 10 minutes after getting out of bed."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She had severe dizziness for about 10 minutes after getting out of bed.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "dizziness"
    # Redundant questions should not be in missing_fields
    assert "severity" not in data["missing_fields"]
    assert "duration" not in data["missing_fields"]
    assert "onset" not in data["missing_fields"]

def test_scenario_c_near_fall_strict_classification(client):
    # Scenario C: "She almost fell near the bathroom."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She almost fell near the bathroom.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "near_fall"
    assert data["category"] != "fall"

def test_scenario_d_explicit_fall_classification(client):
    # Scenario D: "She fell down in the bathroom."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She fell down in the bathroom.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "fall"

def test_scenario_e_cognition_no_dementia_diagnosis(client):
    # Scenario E: "She seems confused today."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She seems confused today.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "cognition"

    # Complete session
    comp = client.post(f"/api/clarification/{data['session_id']}/complete").json()
    struct = comp["structured_observation"]
    assert struct.get("dementia_diagnosed") is False
    assert struct.get("clinical_diagnoses_inferred") is False

def test_scenario_f_nutrition_intake(client):
    # Scenario F: "She didn't eat much at dinner."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She didn't eat much at dinner.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "nutrition"
    assert data["observation"]["extracted_attributes"].get("meal") == "Dinner"

def test_scenario_g_medication_uncertainty(client):
    # Scenario G: "I think she took her medicine."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "I think she took her medicine.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    assert data["category"] == "medication_adherence"
    assert data["observation"]["certainty"] == "UNCERTAIN"
    assert data["observation"]["confidence"] == "LOW"

def test_scenario_h_weakness_no_inferred_etiology(client):
    # Scenario H: "She is weak."
    res = client.post("/api/observations/start", json={
        "patient_code": "P001",
        "text": "She is weak.",
        "processing_mode": "LLM"
    })
    assert res.status_code == 201
    data = res.json()
    comp = client.post(f"/api/clarification/{data['session_id']}/complete").json()
    struct = comp["structured_observation"]
    assert "anemia" not in str(struct).lower()
    assert "infection" not in str(struct).lower()
    assert "dehydration" not in str(struct).lower()
    assert struct.get("clinical_diagnoses_inferred") is False
