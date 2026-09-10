# EvoCare Architecture

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

EvoCare separates raw human signals from clinical records and AI-derived synthesis. This document details the 6-layer memory architecture that underpins the evolving Patient Wiki.

---

## 1. Architectural Flow Diagram

```
                 +-------------------------------------------------+
                 |                  RAW EVIDENCE                   |
                 |  - Doctor Encounters (EV-DR-*)                  |
                 |  - Caregiver Observations (EV-CG-*)             |
                 |  - Lab Biomarkers (EV-LAB-*)                    |
                 |  - Medication Regimens (EV-MED-*)               |
                 |  - Patient Reports (EV-PAT-*, EV-MR-*)          |
                 +-------------------------------------------------+
                                          |
                                          v
                 +-------------------------------------------------+
                 |                STRUCTURED MEMORY                |
                 |  - Schema Validation & Entity Extraction        |
                 |  - Ambiguity & Missing Field Detection          |
                 |  - Source Tagging & Immutability Enforcement    |
                 +-------------------------------------------------+
                                          |
                                          v
                 +-------------------------------------------------+
                 |                  PATIENT WIKI                   |
                 |  - Clinical Subspace (Diagnoses, Labs, Meds)    |
                 |  - Caregiver Subspace (Mobility, Sleep, Eating) |
                 |  - Bidirectional Cross-Wiki Hyperlinks          |
                 +-------------------------------------------------+
                                          |
                                          v
                 +-------------------------------------------------+
                 |                 BASELINE ENGINE                 |
                 |  - Immutable Functional Baseline Anchor         |
                 |  - Delta & Deviation Tracking                   |
                 +-------------------------------------------------+
                                          |
                                          v
                 +-------------------------------------------------+
                 |                 TREND & CONFLICT                |
                 |  - Temporal Trajectory Modeling                 |
                 |  - Caregiver vs. Clinician Conflict Matrix      |
                 |  - Resolution Flagging                          |
                 +-------------------------------------------------+
                                          |
                                          v
                 +-------------------------------------------------+
                 |              PATIENT MEMORY SUMMARY             |
                 |  - High-level Longitudinal Synthesis            |
                 |  - Clinician Decision Support Anchor            |
                 +-------------------------------------------------+
```

---

## 2. The Four Tenets of EvoCare

```
+--------------------------------------------------------------------------+
|  LLM INTERPRETS  |  Translates colloquial caregiver speech and clinical  |
|                  |  shorthand into structured observations and trends.   |
+------------------+-------------------------------------------------------+
|  EVIDENCE PROVES |  Every derived assertion links directly to immutable  |
|                  |  Evidence IDs (EV-*). Zero ungrounded generation.     |
+------------------+-------------------------------------------------------+
|  MEMORY EVOLVES  |  Maintains historical context, incorporates updates,  |
|                  |  preserves baseline, and tracks functional deltas.    |
+------------------+-------------------------------------------------------+
|  DOCTOR DECIDES  |  System flags deviations and conflicts but leaves all |
|                  |  clinical diagnoses and treatment decisions to MDs.   |
+------------------+-------------------------------------------------------+
```

---

## 3. Layer Descriptions

### Layer 1: Raw Evidence Ingestion
Captures untransformed inputs with strict metadata (`Evidence ID`, `Patient ID`, `Source Type`, `Source ID`, `Observed At`, `Recorded At`, `Original Statement`, `Status`). Once committed, raw evidence is permanent and immutable.

### Layer 2: Structured Memory & Normalization
Applies clinical domain parsing. If a caregiver submits a vague observation (e.g., *"He is dizzy"*), the system flags missing parameters (`duration`, `severity`, `trigger`) as `UNKNOWN` rather than guessing.

### Layer 3: The Evolving Patient Wiki
Maintains domain-specific Wiki articles organized into two primary namespaces:
- `Clinical/`: Grounded exclusively in doctor notes, lab sheets, and prescription records.
- `Caregiver/`: Grounded in daily family observations, symptom reports, and behavioral notes.

### Layer 4: Baseline Engine
Maintains an immutable snapshot of the patient's habitual physiological, cognitive, and functional status. Observations are evaluated against this baseline to calculate clinical deltas.

### Layer 5: Trend & Conflict Detection
Analyzes the temporal velocity of changes (e.g., progressive mobility decline vs. acute recovery). Identifies discrepancies between clinician clinic-visit impressions and real-world caregiver logs.

### Layer 6: Patient Memory Synthesis
Generates dynamic clinical executive briefs that highlight baseline deviations, emerging risks, recent improvements, and unresolved ambiguities for attending physicians.

---

## 4. Key Cross-References
- [[Data Model]]
- [[Source Types]]
- [[Memory Rules]]
- [[Timeline]]
- [[Patient Wiki/P001 Meenakshi Raman/Patient Overview|Patient Overview]]
