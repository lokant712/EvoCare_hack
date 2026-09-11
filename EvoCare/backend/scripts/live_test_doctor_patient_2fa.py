import requests

BASE_URL = "http://localhost:8000/api"

def test_flow():
    # 1. Login as doctor.demo
    login_res = requests.post(f"{BASE_URL}/auth/login", json={"username": "doctor.demo", "password": "DoctorPass123!"})
    print("Login:", login_res.status_code)
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Lookup P001
    lookup_res = requests.get(f"{BASE_URL}/patients/lookup/P001", headers=headers)
    print("Lookup P001:", lookup_res.status_code, lookup_res.json())

    # 3. Request Access Code
    req_res = requests.post(f"{BASE_URL}/patients/request-access-code", json={"patient_code": "P001"}, headers=headers)
    print("Request Access Code:", req_res.status_code, req_res.json())
    code = req_res.json()["demo_code"]

    # 4. Verify invalid code
    bad_res = requests.post(f"{BASE_URL}/patients/verify-access-code", json={"patient_code": "P001", "verification_code": "000000"}, headers=headers)
    print("Bad Code verify (expect 400):", bad_res.status_code)

    # 5. Verify valid code
    good_res = requests.post(f"{BASE_URL}/patients/verify-access-code", json={"patient_code": "P001", "verification_code": code}, headers=headers)
    print("Good Code verify:", good_res.status_code, good_res.json())

if __name__ == "__main__":
    test_flow()
