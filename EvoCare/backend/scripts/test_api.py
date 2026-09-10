import sys
import os
from pathlib import Path
from fastapi.testclient import TestClient

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.main import app

def run_api_tests():
    client = TestClient(app)
    print("=====================================")
    print("RUNNING EVOCARE FASTAPI ENDPOINT TESTS")
    print("=====================================")

    endpoints = [
        ("GET /health", "/health", 200),
        ("GET /api/patients", "/api/patients", 200),
        ("GET /api/patients/1", "/api/patients/1", 200),
        ("GET /api/patients/1/summary", "/api/patients/1/summary", 200),
        ("GET /api/patients/1/clinical", "/api/patients/1/clinical", 200),
        ("GET /api/patients/1/caregiver-observations", "/api/patients/1/caregiver-observations", 200),
        ("GET /api/patients/1/evidence", "/api/patients/1/evidence", 200),
        ("GET /api/evidence/EV-CG-031", "/api/evidence/EV-CG-031", 200),
        ("GET /api/patients/1/medications", "/api/patients/1/medications", 200),
        ("GET /api/patients/1/labs", "/api/patients/1/labs", 200),
        ("GET /api/patients/1/baseline", "/api/patients/1/baseline", 200),
        ("GET /api/patients/1/patterns", "/api/patients/1/patterns", 200),
        ("GET /api/patients/1/conflicts", "/api/patients/1/conflicts", 200),
        ("GET /api/patients/1/memory", "/api/patients/1/memory", 200),
        ("GET /api/patients/1/timeline", "/api/patients/1/timeline", 200),
        ("GET /api/patterns/1/evidence", "/api/patterns/1/evidence", 200),
        ("GET /api/conflicts/1/evidence", "/api/conflicts/1/evidence", 200),
    ]

    passed = 0
    failed = 0

    for name, path, expected_status in endpoints:
        resp = client.get(path)
        if resp.status_code == expected_status:
            print(f"[PASS] {name} -> Status {resp.status_code}")
            passed += 1
        else:
            print(f"[FAIL] {name} -> Expected {expected_status}, Got {resp.status_code}: {resp.text}")
            failed += 1

    print("-------------------------------------")
    print(f"Results: {passed} passed, {failed} failed")
    if failed == 0:
        print("ALL API ENDPOINTS TESTED SUCCESSFULLY!")
    return failed == 0

if __name__ == "__main__":
    success = run_api_tests()
    sys.exit(0 if success else 1)
