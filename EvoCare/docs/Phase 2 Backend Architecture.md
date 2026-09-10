# Phase 2 Backend Architecture: EvoCare Longitudinal Patient Memory System

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Patient: Meenakshi Raman (`P001`) | Age: 78 | Location: Chennai, TN

---

## 1. System Overview

Phase 2 builds the **Backend Foundation, Relational Database, and REST API** layer for the EvoCare platform. It takes the multi-source Markdown Wiki and Evidence hierarchy created in Phase 1 and converts it into a typed, normalized, and immutable relational memory model.

```
+-------------------------------------------------------------------------------+
|                       OBSIDIAN KNOWLEDGE BASE (PHASE 1)                       |
|   Raw Evidence/ (EV-CG-*, EV-DR-*, EV-LAB-*, EV-MED-*, EV-PAT-*, EV-MR-*)     |
|   Patient Wiki/ (Clinical/, Caregiver/, Derived/)                             |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                        IMPORTER (ImportService)                               |
|   - Regex & Markdown AST Parser                                               |
|   - Schema Normalization & Entity Mapping                                     |
|   - Multi-Source Segregation Validator                                        |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                   SQLAlchemy ORM & SQLite RELATIONAL STORE                    |
|   - Patient, Evidence, Observation, CaregiverObservation, DoctorRecord       |
|   - Medication, LabRecord, Baseline, Pattern, Conflict, MemoryPage, AuditLog  |
|   - Association Junctions (pattern_evidence, conflict_evidence, etc.)         |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                   PYDANTIC V2 DATA SCHEMAS & SERVICES                         |
|   - Strict Type Validation & Serializers                                      |
|   - ProvenanceService (Why? / Evidence Graph Traversal)                       |
|   - MemoryService (Longitudinal Timeline & Multi-Stream Memory Slices)       |
+-------------------------------------------------------------------------------+
                                       |
                                       v
+-------------------------------------------------------------------------------+
|                     FASTAPI RESTful API & SWAGGER DOCS                        |
|   /health, /api/patients, /api/evidence, /api/caregiver-observations          |
|   /api/clinical, /api/medications, /api/labs, /api/timeline, /api/patterns... |
+-------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Pillars

### 2.1 Immutability of Raw Evidence
- Every piece of incoming information is stored as an `Evidence` row (`EV-CG-*`, `EV-DR-*`, etc.).
- There are **no update or delete endpoints** exposed for evidence.
- The `status` field is set to `IMMUTABLE`.
- If a correction occurs, it is appended as a new evidence entity rather than overwriting historical truth.

### 2.2 Strict Source Stream Segregation
- **Clinical Records (`DoctorRecord`)**: High clinical authority, clinician-confirmed facts.
- **Caregiver Observations (`CaregiverObservation`)**: Real-world context, functional notes. Never auto-converted into medical diagnoses.
- **Biomarkers (`LabRecord`)**: Quantitative laboratory parameters with reference ranges.
- **Derived Patterns (`Pattern`)**: Machine-derived longitudinal patterns citing explicit evidence IDs. Marked `AI_DERIVED`.

### 2.3 Immutable Baseline Anchoring
- `Baseline` represents the long-term functional reference point (e.g., independent mobility, normal cognition).
- Observations that deviate from baseline are modeled as *trajectories* without destroying or overwriting the baseline.

### 2.4 Traceable Provenance Chains
- Every `Pattern`, `Conflict`, and `Observation` is mapped to its supporting `Evidence` IDs via database foreign keys and junction tables.
- Querying `/api/patterns/{id}/evidence` returns the exact source documents, authors, and timestamps that justify the pattern.

---

## 3. Database Schema Entities & Relationships

| Table Name | Description | Key Columns | Relationships |
| :--- | :--- | :--- | :--- |
| `patients` | Primary patient entity | `id`, `patient_code`, `name`, `age`, `sex`, `location`, `status`, `is_synthetic` | Has many Evidences, Observations, Baselines, etc. |
| `evidences` | Immutable raw data units | `id`, `patient_id`, `evidence_code`, `source_type`, `source_id`, `observed_at`, `recorded_at`, `original_statement`, `status` | Belongs to Patient; Has many observations |
| `caregiver_observations` | Caregiver daily logs | `id`, `patient_id`, `evidence_id`, `caregiver_id`, `category`, `observation_text`, `attributes`, `observed_at`, `information_state` | Belongs to Patient & Evidence |
| `doctor_records` | Clinical progress notes | `id`, `patient_id`, `evidence_id`, `doctor_id`, `record_type`, `content`, `observed_at` | Belongs to Patient & Evidence |
| `medications` | Pharmacy prescriptions | `id`, `patient_id`, `evidence_id`, `name`, `dose`, `frequency`, `status`, `indication` | Belongs to Patient & Evidence |
| `lab_records` | Pathology biomarkers | `id`, `patient_id`, `evidence_id`, `test_panel`, `test_name`, `value`, `unit`, `reference_range`, `observed_at` | Belongs to Patient & Evidence |
| `baselines` | Immutable functional anchors | `id`, `patient_id`, `category`, `baseline_value`, `information_state` | Many-to-many with Evidence via `baseline_evidence` |
| `patterns` | Longitudinal trend models | `id`, `patient_id`, `category`, `title`, `description`, `status`, `detected_at` | Many-to-many with Evidence via `pattern_evidence` |
| `conflicts` | Multi-source discrepancies | `id`, `patient_id`, `category`, `title`, `description`, `doctor_view`, `caregiver_view`, `status` | Many-to-many with Evidence via `conflict_evidence` |
| `memory_pages` | Wiki markdown mirror | `id`, `patient_id`, `path`, `title`, `content`, `page_type`, `version` | Belongs to Patient |

---

## 4. API Endpoints Reference

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | System health check and API metadata |
| `GET` | `/api/patients` | List all patients |
| `GET` | `/api/patients/{id}` | Get patient demographic details |
| `GET` | `/api/patients/{id}/summary` | Executive summary (Baseline, Diagnoses, Meds, Recent Obs, Trends, Conflicts) |
| `GET` | `/api/patients/{id}/evidence` | Filterable evidence log (`source_type`, `category`, `date_from`, `date_to`) |
| `GET` | `/api/evidence/{evidence_id}` | Retrieve individual immutable evidence record by ID or code |
| `GET` | `/api/patients/{id}/caregiver-observations` | Caregiver observation stream with category & temporal filtering |
| `GET` | `/api/patients/{id}/clinical` | Segregated clinical summary (Diagnoses, Doctor Records, Medical History, Labs) |
| `GET` | `/api/patients/{id}/medications` | Active and PRN prescription list |
| `GET` | `/api/patients/{id}/labs` | Serial laboratory biomarker measurements |
| `GET` | `/api/patients/{id}/baseline` | Patient functional baseline profiles |
| `GET` | `/api/patients/{id}/patterns` | Derived longitudinal trend patterns |
| `GET` | `/api/patients/{id}/conflicts` | Unresolved multi-source clinical differences |
| `GET` | `/api/patients/{id}/memory` | Comprehensive structured longitudinal memory object |
| `GET` | `/api/patients/{id}/timeline` | Chronological event stream across all modalities |
| `GET` | `/api/patterns/{id}/evidence` | Provenance chain for a specific derived pattern |
| `GET` | `/api/conflicts/{id}/evidence` | Provenance chain for a specific multi-source conflict |
| `GET` | `/api/observations/{id}/evidence` | Provenance record for an individual observation |

---

## 5. Migration Path to PostgreSQL
The models are written using standard SQLAlchemy 2.0 column definitions and relationships without SQLite-specific dialect locks. Migrating to PostgreSQL in future phases requires only:
1. Updating `DATABASE_URL` in `.env` to `postgresql://user:pass@host:5432/evocare`.
2. Running Alembic migrations to generate PostgreSQL schemas.
