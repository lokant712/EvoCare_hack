import requests

BASE_URL = "http://localhost:8000/api"

def run_tests():
    print("=== Testing 5 Demo Patients & Gmail 2FA ===")
    # 1. Login as doctor
    doc_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "doctor.demo", "password": "DoctorPass123!"})
    assert doc_login.status_code == 200, f"Doctor login failed: {doc_login.text}"
    doc_token = doc_login.json()["access_token"]
    doc_headers = {"Authorization": f"Bearer {doc_token}"}

    # 2. Check all 5 demo patients
    for p_code in ["P001", "P002", "P003", "P004", "P005"]:
        res = requests.get(f"{BASE_URL}/patients/lookup/{p_code}", headers=doc_headers)
        assert res.status_code == 200, f"Lookup failed for {p_code}: {res.text}"
        data = res.json()
        print(f"Patient {p_code}: {data['name']}, Age: {data['age']}, Email: {data['email']}")
        assert data['email'] == "lokanthsrihari7@gmail.com", f"Expected lokanthsrihari7@gmail.com, got {data['email']}"

    # 3. Request 2FA Code for P003 (Rajesh Varma)
    req_res = requests.post(f"{BASE_URL}/patients/request-access-code", json={"patient_code": "P003"}, headers=doc_headers)
    assert req_res.status_code == 200, f"Request code failed: {req_res.text}"
    req_data = req_res.json()
    print("Requested 2FA Code for P003:", req_data)
    assert req_data["patient_email"] == "lokanthsrihari7@gmail.com"
    otp = req_data["demo_code"]

    # 4. Verify 2FA code
    verify_res = requests.post(f"{BASE_URL}/patients/verify-access-code", json={"patient_code": "P003", "verification_code": otp}, headers=doc_headers)
    assert verify_res.status_code == 200, f"Verify 2FA failed: {verify_res.text}"
    print("Doctor 2FA verification for P003: SUCCESS")

    print("\n=== Testing Patient & Caretaker Connection Workflow ===")
    # 5. Login as patient (patient.demo)
    pat_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "patient.demo", "password": "PatientPass123!"})
    assert pat_login.status_code == 200, f"Patient login failed: {pat_login.text}"
    pat_token = pat_login.json()["access_token"]
    pat_headers = {"Authorization": f"Bearer {pat_token}"}

    # 6. Get available caregivers
    cgs_res = requests.get(f"{BASE_URL}/caregiver-connections/caregivers", headers=pat_headers)
    assert cgs_res.status_code == 200
    caregivers = cgs_res.json()
    print("Available Caregivers:", [(c['id'], c['username'], c['full_name']) for c in caregivers])
    cg_id = caregivers[0]['id']

    # 7. Patient requests pairing with caregiver
    pair_res = requests.post(f"{BASE_URL}/caregiver-connections/request", json={"patient_code": "P001", "caregiver_user_id": cg_id, "notes": "Daily morning vitals assist"}, headers=pat_headers)
    assert pair_res.status_code == 200
    print("Pairing requested:", pair_res.json())

    # 8. Login as caregiver
    cg_login = requests.post(f"{BASE_URL}/auth/login", json={"username": "caregiver.demo", "password": "CaregiverPass123!"})
    assert cg_login.status_code == 200
    cg_token = cg_login.json()["access_token"]
    cg_headers = {"Authorization": f"Bearer {cg_token}"}

    # 9. Caregiver checks incoming connections
    my_conns = requests.get(f"{BASE_URL}/caregiver-connections/my-connections", headers=cg_headers).json()
    print("Caregiver connections count:", len(my_conns))
    pending_conn = [c for c in my_conns if c['status'] == 'PENDING']
    assert len(pending_conn) > 0, "Expected at least 1 pending connection"
    conn_id = pending_conn[0]['id']

    # 10. Caregiver approves pairing
    approve_res = requests.post(f"{BASE_URL}/caregiver-connections/{conn_id}/respond", json={"action": "APPROVE"}, headers=cg_headers)
    assert approve_res.status_code == 200
    print("Caregiver approved pairing:", approve_res.json())

    # 11. Verify persistent grant in authorized-patients
    auth_pats = requests.get(f"{BASE_URL}/auth/authorized-patients", headers=cg_headers).json()
    print("Caregiver authorized patients after approval:", [p['patient_code'] for p in auth_pats])
    assert any(p['patient_code'] == 'P001' for p in auth_pats)

    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
