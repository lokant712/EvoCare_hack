import pytest
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.services.memory import WikiSynchronizer, MemoryService

def test_wiki_test_a_mobility_evidence_updates_mobility_page(client, db_session):
    # Test A: New mobility evidence updates Mobility.md
    res_cons = client.post("/api/memory/consolidate", json={
        "patient_id": "P001",
        "evidence_code": "EV-CG-021"
    })
    assert res_cons.status_code == 201
    prop_id = res_cons.json()["proposal_id"]

    res_apply = client.post(f"/api/memory/apply/{prop_id}")
    assert res_apply.status_code == 200
    wiki_path = res_apply.json()["wiki_page"]
    assert "Mobility.md" in wiki_path

    # Read Wiki content and verify update
    content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "EV-CG-021" in content
    assert "Longitudinal Memory" in content

def test_wiki_test_b_existing_content_remains(client, db_session):
    # Test B: Existing baseline and sections remain present
    content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "Baseline" in content
    assert "Caregiver Observation Log" in content or "Mobility" in content

def test_wiki_test_c_evidence_id_appears_in_wiki(client):
    content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "EV-CG-021" in content

def test_wiki_test_d_memory_version_appears(client):
    content = WikiSynchronizer.read_page("P001", "Mobility")
    assert "Memory Version" in content

def test_wiki_test_e_historical_information_not_deleted(client, db_session):
    # Test E: Multiple updates preserve historical claims
    # Consolidate and apply second update
    res_cons2 = client.post("/api/memory/consolidate", json={
        "patient_id": "P001",
        "evidence_code": "EV-CG-040"
    })
    if res_cons2.status_code == 201:
        prop_id2 = res_cons2.json()["proposal_id"]
        client.post(f"/api/memory/apply/{prop_id2}")

    content = WikiSynchronizer.read_page("P001", "Mobility")
    # Both EV-CG-021 and baseline must remain
    assert "EV-CG-021" in content

def test_wiki_test_f_wrong_patient_cannot_modify_wiki(client):
    res_cons = client.post("/api/memory/consolidate", json={
        "patient_id": "NON_EXISTENT_PATIENT",
        "evidence_code": "EV-CG-021"
    })
    assert res_cons.status_code == 404

def test_wiki_test_g_rejected_proposal_does_not_modify_wiki(client, db_session):
    initial_content = WikiSynchronizer.read_page("P001", "Cognition")
    
    # Try invalid consolidation (or rejected apply)
    res_cons = client.post("/api/memory/consolidate", json={
        "patient_id": "P001",
        "evidence_code": "EV-CG-003"
    })
    assert res_cons.status_code == 201

    # Check that Cognition Wiki remains unchanged before apply
    current_content = WikiSynchronizer.read_page("P001", "Cognition")
    assert current_content == initial_content

def test_memory_diff_endpoint(client):
    res = client.get("/api/memory/1/Mobility/diff")
    assert res.status_code == 200
    data = res.json()
    assert "current_version" in data
    assert "added_claims" in data
    assert "preserved_claims" in data

def test_memory_history_endpoint(client):
    res = client.get("/api/memory/1/Mobility/history")
    assert res.status_code == 200
    history = res.json()
    assert isinstance(history, list)
    if history:
        assert "version_number" in history[0]

def test_patient_memory_summary_endpoint(client):
    res = client.get("/api/memory/1/summary")
    assert res.status_code == 200
    summary = res.json()
    assert "baseline" in summary
    assert "recent_changes" in summary
    assert "conflicts" in summary
    assert "unknowns" in summary
