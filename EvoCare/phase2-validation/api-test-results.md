# EvoCare Phase 2 API Test Results

> **Test Execution Run: 2026-09-10**  
> Test Client: FastAPI `TestClient` (HTTPX Engine)

---

## Summary Table

| Endpoint | Method | Expected Status | Actual Status | Result | Response Payload Highlights |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `/health` | `GET` | 200 | 200 | **PASS** | `{"status": "ok", "project": "EvoCare Longitudinal Patient Memory System"}` |
| `/api/patients` | `GET` | 200 | 200 | **PASS** | Returns list containing synthetic patient `P001` (`Meenakshi Raman`, 78F) |
| `/api/patients/1` | `GET` | 200 | 200 | **PASS** | Returns patient demographics, location: `Chennai, Tamil Nadu` |
| `/api/patients/1/summary` | `GET` | 200 | 200 | **PASS** | Aggregated object with 4 diagnoses, 4 active meds, baseline, recent obs & trends |
| `/api/patients/1/clinical` | `GET` | 200 | 200 | **PASS** | Strict clinician subspace: 4 diagnoses, 5 doctor records, 15 lab values, 4 meds |
| `/api/patients/1/caregiver-observations` | `GET` | 200 | 200 | **PASS** | Returns 47 caregiver records from CG001, CG002, and CG003 |
| `/api/patients/1/evidence` | `GET` | 200 | 200 | **PASS** | Returns 65 immutable raw evidence records with timestamps & source tags |
| `/api/evidence/EV-CG-031` | `GET` | 200 | 200 | **PASS** | Returns verbatim statement: *"She almost fell near the bathroom but I caught her."* |
| `/api/patients/1/medications` | `GET` | 200 | 200 | **PASS** | Returns Metformin 500mg, Amlodipine 5mg, Atorvastatin 10mg, Paracetamol 500mg |
| `/api/patients/1/labs` | `GET` | 200 | 200 | **PASS** | Returns serial lab panels with HbA1c trajectory (7.1% -> 7.3% -> 7.4%) |
| `/api/patients/1/baseline` | `GET` | 200 | 200 | **PASS** | Returns 9 functional baselines (independent mobility anchor preserved) |
| `/api/patients/1/patterns` | `GET` | 200 | 200 | **PASS** | Returns 7 derived pattern models citing supporting evidence IDs |
| `/api/patients/1/conflicts` | `GET` | 200 | 200 | **PASS** | Returns 3 documented clinical vs. caregiver differences |
| `/api/patients/1/memory` | `GET` | 200 | 200 | **PASS** | Full longitudinal memory snapshot with executive brief and recovery notes |
| `/api/patients/1/timeline` | `GET` | 200 | 200 | **PASS** | Chronological multi-stream events from 2025-10 to 2026-09 |
| `/api/patterns/1/evidence` | `GET` | 200 | 200 | **PASS** | Returns pattern title and full supporting evidence array with source types |
| `/api/conflicts/1/evidence` | `GET` | 200 | 200 | **PASS** | Returns doctor view, caregiver view, and underlying evidence records |
| `/api/observations/1/evidence` | `GET` | 200 | 200 | **PASS** | Returns atomic raw evidence record corresponding to observation |

---

## Immutability Endpoint Checks

| Attempted Operation | Expected Result | Actual Result | Verification |
| :--- | :--- | :--- | :--- |
| `PUT /api/evidence/EV-CG-031` | `405 Method Not Allowed` | `405` | **PASS (Immutability enforced)** |
| `DELETE /api/evidence/EV-CG-031` | `405 Method Not Allowed` | `405` | **PASS (Deletion prohibited)** |
| `PATCH /api/evidence/EV-DR-001` | `405 Method Not Allowed` | `405` | **PASS (Patching prohibited)** |
