import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)

def test_full_flow():
    print("=== 1. Testing Doctor Login & 5 Demo Patients ===")
    login_res = client.post("/api/auth/login", json={"username": "doctor.demo", "password": "DoctorPass123!"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    doc_token = login_res.json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # Verify all 5 demo patients
    for code in ["P001", "P002", "P003", "P004", "P005"]:
        lookup = client.get(f"/api/patients/lookup/{code}", headers=doc_headers)
        assert lookup.status_code == 200, f"Lookup failed for {code}: {lookup.text}"
        data = lookup.json()
        print(f"  [OK] {code}: {data['name']} (Age: {data['age']}, Email: {data['email']})")
        assert data["email"] == "lokanthsrihari7@gmail.com"

    print("\n=== 2. Testing Gmail 2FA Verification for P003 (Rajesh Varma) ===")
    req_res = client.post("/api/patients/request-access-code", json={"patient_code": "P003"}, headers=doc_headers)
    assert req_res.status_code == 200
    req_data = req_res.json()
    print(f"  [OK] Code generated: {req_data['demo_code']} -> Dispatched to {req_data['patient_email']}")
    assert req_data["patient_email"] == "lokanthsrihari7@gmail.com"

    verify_res = client.post("/api/patients/verify-access-code", json={"patient_code": "P003", "verification_code": req_data["demo_code"]}, headers=doc_headers)
    assert verify_res.status_code == 200
    print(f"  [OK] Verified: {verify_res.json()['message']}")

    print("\n=== 3. Testing Patient & Caretaker Connection / Pairing Workflow ===")
    # Login as patient.demo
    pat_login = client.post("/api/auth/login", json={"username": "patient.demo", "password": "PatientPass123!"})
    assert pat_login.status_code == 200
    pat_token = pat_login.json()["access_token"]
    pat_headers = {"Authorization": f"Bearer {pat_token}"}

    # Get available caregivers
    cgs = client.get("/api/caregiver-connections/caregivers", headers=pat_headers).json()
    assert len(cgs) > 0
    cg_id = cgs[0]["id"]
    print(f"  [OK] Found caregiver: {cgs[0]['full_name']} (@{cgs[0]['username']})")

    # Patient requests pairing for P002
    pair_req = client.post("/api/caregiver-connections/request", json={"patient_code": "P002", "caregiver_user_id": cg_id, "notes": "Memory support and evening walk"}, headers=pat_headers)
    assert pair_req.status_code == 200
    print(f"  [OK] Pairing request sent: {pair_req.json()['message']}")

    # Login as caregiver
    cg_login = client.post("/api/auth/login", json={"username": "caregiver.demo", "password": "CaregiverPass123!"})
    assert cg_login.status_code == 200
    cg_token = cg_login.json()["access_token"]
    cg_headers = {"Authorization": f"Bearer {cg_token}"}

    # Caregiver views pending requests
    conns = client.get("/api/caregiver-connections/my-connections", headers=cg_headers).json()
    pending = [c for c in conns if c["status"] == "PENDING"]
    assert len(pending) > 0
    conn_id = pending[0]["id"]
    print(f"  [OK] Caregiver received request #{conn_id} from {pending[0]['patient_name']}")

    # Caregiver approves pairing
    approve = client.post(f"/api/caregiver-connections/{conn_id}/respond", json={"action": "APPROVE"}, headers=cg_headers)
    assert approve.status_code == 200
    print(f"  [OK] Approved: {approve.json()['message']}")

    # Verify persistent access grant
    auth_pats = client.get("/api/auth/authorized-patients", headers=cg_headers).json()
    codes = [p["patient_code"] for p in auth_pats]
    print(f"  [OK] Caregiver authorized patient codes: {codes}")
    assert "P001" in codes

    # Test disconnection
    disc = client.post(f"/api/caregiver-connections/{conn_id}/disconnect", headers=cg_headers)
    assert disc.status_code == 200
    print(f"  [OK] Disconnected: {disc.json()['message']}")

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    test_full_flow()
