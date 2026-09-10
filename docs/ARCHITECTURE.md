# EvoCare — System Architecture & Data Flow

```
+-----------------------------------------------------------------------------------+
|                                 DOCTOR & USER INTERFACES                          |
|                                                                                   |
|  +-------------------------+  +----------------------------+  +----------------+  |
|  | Doctor Dashboard (Vite) |  | Living Memory Wiki (React) |  | Security & Auth|  |
|  +-------------------------+  +----------------------------+  +----------------+  |
+------------------------------------------+----------------------------------------+
                                           | HTTP / REST (JWT Bearer Auth)
                                           v
+-----------------------------------------------------------------------------------+
|                        FASTAPI APPLICATION & SECURITY GATEWAY                     |
|                                                                                   |
|  +-----------------------+  +-----------------------+  +-----------------------+  |
|  | SecurityHeadersMiddleware |  | JWT Authenticator     |  | PatientAccessGuard    |  |
|  +-----------------------+  +-----------------------+  +-----------------------+  |
|                                                                                   |
|  Routers:                                                                         |
|  /api/auth                /api/dashboard           /api/clinical-reasoning        |
|  /api/memory              /api/observations        /api/timeline                  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                        CLINICAL REASONING & MEMORY SERVICES                       |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | ClinicalContextService: Filter & rank patient context by relevance          |  |
|  +-----------------------------------------------------------------------------+  |
|  | ClinicalReasoningValidator: Strict rule-based safety engine                 |  |
|  | - Prohibits autonomous diagnoses                                           |  |
|  | - Prohibits unauthorized medication changes                                 |  |
|  | - Prohibits hallucinated causal leaps                                       |  |
|  | - Blocks prompt injection attacks                                           |  |
|  +-----------------------------------------------------------------------------+  |
|  | WikiSynchronizer: Markdown living wiki synchronization                       |  |
|  | ProvenanceService: Bidirectional evidence trace generation                  |  |
+------------------------------------------+----------------------------------------+
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                     IMMUTABLE DATA & EVIDENCE REPOSITORY (SQLITE)                 |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  | RAW EVIDENCE STORE: Evidences (Status: IMMUTABLE)                           |  |
|  | - DOCTOR records (Assessments, Labs, Medications)                           |  |
|  | - CAREGIVER observations (Home mobility, sleep, falls, cognition)           |  |
|  +-----------------------------------------------------------------------------+  |
|  | TEMPORAL MEMORY STORE: MemoryClaims, MemoryVersions, MemoryPages            |  |
|  | - Claims link to exact evidence IDs                                         |  |
|  | - Versions track evolution over time                                        |  |
|  +-----------------------------------------------------------------------------+  |
|  | SECURITY & AUDIT STORE: Users, PatientAccessGrants, AuditLogs, SecurityEvents|  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 1. Architectural Philosophy

EvoCare enforces 5 inviolable architectural principles:

1. **LLM Interprets**: Language models summarize, highlight patterns, and suggest differential considerations.
2. **Rules Constrain**: Deterministic code checks all outputs against strict clinical safety invariants before returning to the UI.
3. **Evidence Proves**: Every statement or claim must trace to an immutable evidence record with observer, timestamp, and source text.
4. **Memory Evolves**: Patient states are tracked longitudinally across versioned snapshots. Past states are never overwritten or deleted.
5. **Doctor Decides**: EvoCare never prescribes, never alters clinical records, and never issues definitive final diagnoses.

---

## 2. Core Subsystems

### Subsystem 1: Ingestion & Evidence Immutability (Phase 1–3)
- Ingests structured clinical records (ICD-10, RXNorm, LOINC) and unstructured caregiver observations.
- Each item is assigned an immutable evidence code (`EV-DR-xxx` or `EV-CG-xxx`).
- Evidence rows are strictly append-only.

### Subsystem 2: Ambiguity Clarification Engine (Phase 3)
- If a caregiver report is vague or ambiguous (e.g. *"She stumbled"*), the clarification engine asks targeted questions before committing the evidence to memory.
- Ensures evidence quality without burdening the clinician.

### Subsystem 3: Longitudinal Living Memory & Wiki Sync (Phase 4–5)
- Organizes health into domains: *Mobility, Falls, Dizziness, Cognition, Nutrition, Sleep, Pain, Behavior, Medication Adherence*.
- Maintains versioned claims (`MemoryVersion 1 -> Version 2`).
- Synchronizes with human-readable Markdown pages in `data/wiki/`.

### Subsystem 4: Doctor Dashboard & Provenance Explorer (Phase 6)
- React / Vite dashboard providing a single pane of glass for doctors.
- The **"Why?"** button opens a modal showing the exact provenance trail for any detected change.
- Visual distinctions for source credibility: Doctor-confirmed vs Caregiver-reported.

### Subsystem 5: Doctor-Only Clinical Reasoning Assistant (Phase 7)
- Allows attending physicians to query trajectory trends.
- Protected by `ClinicalReasoningValidator`:
  - Enforces enum-bounded status: `POSSIBLE_CONSIDERATION`, `INSUFFICIENT_EVIDENCE`.
  - Blocks prompt injection signatures.
  - Generates mandatory missing information reports (*Missing != Normal*).

### Subsystem 6: Security, RBAC & Audit Hardening (Phase 8–9)
- JWT bearer token authentication with bcrypt password hashing.
- Role-based authorization matrix (`DOCTOR`, `CAREGIVER`, `ADMIN`).
- Fine-grained patient-level access grants (`PatientAccess`).
- Tamper-evident, immutable audit trail for all read and query events.
