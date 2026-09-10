# EvoCare Phase 6 Architecture: Doctor Dashboard & Longitudinal Patient View

## 1. System Overview & Objective
Phase 6 delivers the first user-facing workstation interface for EvoCare: the **Doctor Dashboard**. The system synthesizes the three core data layers (Immutable Evidence, Versioned Memory, and Living Patient Wiki) into a prioritized, high-signal clinical view.

```
                    FastAPI Backend (/api/dashboard)
                                   ↓
                   Dashboard Aggregation Service
                   (app/services/dashboard_service.py)
       ┌───────────────────────────┼───────────────────────────┐
       ↓                           ↓                           ↓
Clinical Subsystem          Memory Subsystem           Caregiver Pipeline
(Diagnoses, Meds, Labs)  (Claims, Versions, Wiki)   (Observations, Evidence)
       ↓                           ↓                           ↓
Database & KB Records       Longitudinal Wiki         Immutable Evidence
       └───────────────────────────┼───────────────────────────┘
                                   ↓ HTTP JSON
                         React Doctor Dashboard
                        (Vite + TypeScript + CSS)
```

---

## 2. Core UX Philosophy: "What Changed Recently?"
Clinicians often have limited time to review voluminous caregiver records. The dashboard prioritizes:
1. **Recent Trajectory Changes**: Directional indicators (`IMPROVEMENT`, `DECLINE`, `FLUCTUATION`, `NEW_OBSERVATION`) highlighting recent shifts.
2. **Clinical vs Caregiver Separation**: Clinician-confirmed diagnoses are isolated from caregiver-reported observations.
3. **Traceability & [Why?] Derivation**: Every AI-derived longitudinal claim allows instant tracing down to the raw evidence records and verbatim statements.
4. **Safety Gating**: Prohibits speculative diagnoses (e.g. confusion $\neq$ dementia; near-fall $\neq$ completed fall; dizziness etiology = `UNKNOWN`).

---

## 3. Backend Aggregation Endpoint (`GET /api/dashboard/patients/{patient_id}`)

### Aggregation Payload Structure:
- `patient`: Demographic identity (`patient_code`, `name`, `age`, `sex`, `location`, `dataset_type`).
- `overview`: 6 core health domains (Mobility, Cognition, Nutrition, Dizziness, Falls, Osteoarthritis).
- `recent_changes`: Priority trajectory cards with latest state, previous state, direction, and evidence counts.
- `clinical_diagnoses`: Verified ICD-10 diagnoses with confirmation date and doctor name.
- `medications`: Active prescriptions with dosage, frequency, status, indication, and start date.
- `labs`: Historical laboratory values and reference ranges.
- `caregiver_observations`: Filterable feed of natural language observations from observers (`CG001`, `CG002`, `CG003`).
- `longitudinal_memory`: Active claims, version number, baseline, and known unknowns.
- `timeline`: Unified chronological stream across clinical visits, lab draws, and caregiver notes.
- `conflicts`: Contextual discrepancies with dual doctor vs caregiver perspectives.
- `fall_safety`: Enforces 0 completed falls / 1 near-fall invariant.
- `provenance_map`: Pre-indexed dictionary of evidence details for modal rendering.

---

## 4. Frontend Component Hierarchy
```
App
 └── Dashboard
      ├── Header (Branding, Demographics, Synthetic Demo Badge, Read-Only Pill)
      ├── SafetyAlert (Guardrail disclaimer & non-diagnostic notice)
      ├── PatientOverviewCard (6-domain baseline vs recent status grid)
      ├── RecentChangesPanel (Directional trajectory, evidence chips, [Why?] trigger)
      ├── ClinicalContextPanel (Tabs: Diagnoses, Medications, Lab Timeline)
      ├── CaregiverObservationsPanel (Isolated caregiver natural language feed)
      ├── LongitudinalMemoryPanel (Synthesized claims, version badge, audit history)
      ├── PatientTimeline (Chronological event stream with category filters)
      ├── ConflictCard (Dual-perspective discrepancy cards)
      ├── WhyModal (Full derivation chain from Claim -> Evidence -> Raw Statements)
      └── EvidenceDrawer (Verbatim statement, timestamps, observer, status)
```

---

## 5. Provenance & "Why?" Flow

```
1. Synthesized Claim:
   "Mobility has shown recent variability, with increased support required during earlier outdoor observations followed by later improvement in indoor walking without support."
        ↓
2. Information State:
   AI-DERIVED (Memory Version 27)
        ↓
3. Supporting Evidence Records:
   - EV-CG-021: "She needed someone's arm while walking outside." (2026-09-02)
   - EV-CG-022: "She was holding the dining table while walking to the kitchen." (2026-08-27)
   - EV-CG-040: "She walked normally inside today and did not need support." (2026-09-09)
   - EV-PAT-002: "I usually walk around the house without any walking stick or support." (2026-08-01)
        ↓
4. Verbatim Raw Evidence Text Verified
```

---

## 6. Safety & Clinical Invariants
1. **Read-Only Invariant**: The dashboard does not include mutation or edit controls.
2. **AI-Derived Labeling**: Every derived statement displays an explicit `AI-DERIVED` badge with disclaimer.
3. **Near-Fall Invariant**: Near-falls are strictly classified as near-falls (zero ground impact).
4. **No Hallucinated Diagnoses**: No dementia, stroke, or dehydration etiologies inferred.
5. **Patient Isolation**: Cross-patient queries strictly rejected with HTTP 404.
