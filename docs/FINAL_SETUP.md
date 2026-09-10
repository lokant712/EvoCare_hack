# EvoCare — Final Setup & Installation Guide

EvoCare is a longitudinal health memory and doctor-facing clinical reasoning system that helps clinicians track eldercare trajectories, maintain living wikis of patient condition evolution, and reason safely over conflicting home and clinical observations.

---

## 1. System Requirements

- **Python**: 3.10, 3.11, or 3.12
- **Node.js**: 18.x or 20.x
- **Operating System**: Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
- **Storage**: ~500 MB for repository, dependencies, and SQLite database
- **Memory**: Minimum 4 GB RAM

---

## 2. Fast Track: One-Click Startup

### On Windows:
Double-click `run_demo.bat` or run:
```cmd
run_demo.bat
```

### On Linux / macOS:
```bash
chmod +x run_demo.sh
./run_demo.sh
```

This starts:
- **FastAPI Backend**: `http://127.0.0.1:8000` (Swagger UI at `/docs`)
- **React Frontend**: `http://localhost:9000`

---

## 3. Manual Step-by-Step Installation

### Step A: Backend Setup
```bash
cd EvoCare/backend

# 1. Create and activate virtual environment (optional but recommended)
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize SQLite database & baseline models
python scripts/init_db.py

# 4. Seed Phase 8 security credentials & multi-patient data (P001 & P002)
python scripts/seed_security_demo.py

# 5. Start development API server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step B: Frontend Setup
```bash
cd frontend

# 1. Install Node packages
npm install

# 2. Verify unit tests (25 tests)
npm test -- --run

# 3. Build production bundle (TypeScript compilation + Vite)
npm run build

# 4. Start Vite dev server on port 9000
npm run dev -- --port 9000
```

---

## 4. Verification & Health Checks

Run the automated verification suite from the repository root:
```bash
python scripts/verify_final.py
```
This executes all 8 verification gates:
1. Database Integrity & Multi-Patient Seed State
2. Authentication & JWT Token Security
3. Authorization Matrix & Patient-Level Isolation (P001 vs P002)
4. Doctor Clinical Reasoning & Non-Autonomous Safety Invariants
5. Read-Only Invariants & Zero Database Mutation
6. Longitudinal Provenance Chain (`MEMORY` -> `CLAIM` -> `VERSION` -> `EVIDENCE`)
7. Immutable Security Audit Logging
8. Frontend Build Output Verification

---

## 5. Demo Credentials

| Role | Username | Password | Assigned Patients | Permissions |
| :--- | :--- | :--- | :--- | :--- |
| **Doctor** | `doctor.demo` | `DoctorPass123!` | `P001` (Meenakshi Raman) | Full clinical reasoning, dashboard, evidence, audit |
| **Doctor (Other)** | `doctor.other` | `DoctorPass123!` | `P002` (Ananya Sharma) | Cross-doctor isolation test; cannot access P001 |
| **Caregiver** | `caregiver.demo` | `CaregiverPass123!` | `P001` | Submit observations, view care notes; **no** reasoning |
| **Administrator** | `admin.demo` | `AdminPass123!` | All (Audit only) | Access grants, security audit logs; **no** clinical |

*Notice: All patient data in EvoCare is synthetic demo data. EvoCare is not for live diagnostic use.*
