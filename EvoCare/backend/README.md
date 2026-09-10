# EvoCare Backend & Database (Phase 2)

> **Evolving Patient Health Memory & Clinical Intelligence**  
> Synthetic Patient: Meenakshi Raman (`P001`, 78F, Chennai, TN)

---

## 1. Prerequisites
- **Python**: 3.10, 3.11, or 3.12
- **SQLite3**: Built-in with Python
- **Virtual Environment Tool**: `venv`

---

## 2. Installation & Setup

### Step 1: Create and Activate Virtual Environment
```bash
# Navigate to backend directory
cd EvoCare/backend

# Create virtual environment
python -m venv .venv

# Activate on Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activate on Windows (Command Prompt)
.venv\Scripts\activate.bat

# Activate on Linux / macOS
source .venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

---

## 3. Database Initialization & Importer

### Step 1: Initialize Database Schema
```bash
python scripts/init_db.py
```
*Creates the SQLite schema at `evocare.db` with all tables and foreign key constraints.*

### Step 2: Import Knowledge Base from Phase 1
```bash
python scripts/import_knowledge_base.py
```
*Parses all 65 Markdown evidence files, caregiver logs, doctor records, medications, labs, baselines, patterns, and conflicts into relational tables.*

### Step 3: Verify Database Integrity
```bash
python scripts/verify_import.py
```

---

## 4. Running the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **API Base URL**: `http://localhost:8000`
- **Interactive Swagger Documentation**: `http://localhost:8000/docs`
- **ReDoc Documentation**: `http://localhost:8000/redoc`
- **Health Check**: `http://localhost:8000/health`

---

## 5. Running Automated Tests

```bash
# Run full test suite with verbose output
pytest -v

# Run specific domain test suites
pytest tests/test_caregiver.py -v
pytest tests/test_clinical.py -v
pytest tests/test_provenance.py -v
pytest tests/test_phase2_integrity.py -v
```

---

## 6. Inspecting the Database

The database is stored in `EvoCare/backend/evocare.db`. You can inspect it using the SQLite CLI or tools like **DB Browser for SQLite**:

```bash
sqlite3 evocare.db ".tables"
sqlite3 evocare.db "SELECT patient_code, name, age, location FROM patients;"
sqlite3 evocare.db "SELECT evidence_code, source_type, observed_at FROM evidences LIMIT 10;"
sqlite3 evocare.db "SELECT title, category, status FROM patterns;"
sqlite3 evocare.db "SELECT title, doctor_view, caregiver_view, status FROM conflicts;"
```

---

## 7. Architecture & Phase 2 Boundaries

- **Phase 1**: Obsidian Knowledge Base Markdown Vault (Reference Ground Truth).
- **Phase 2 (Current)**: Relational Database, SQLAlchemy Models, Pydantic Schemas, FastAPI REST APIs, Immutability Guarantees, Provenance Engine.
- **Phase 3 (Next)**: Caregiver Multimodal Ingestion (Voice/Text/WhatsApp), Ambient Input, and Ambiguity Clarification.
- **Phase 4 (Future)**: Doctor Longitudinal Dashboard with Temporal Scrubbing.
- **Phase 5 (Future)**: Clinical Reasoning Assistant & EHR Integration.
