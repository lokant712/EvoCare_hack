import os
import shutil

BASE_DIR = r"c:\Users\lokan\Downloads\journey\sve\EvoCare-Knowledge-Base"

def write_file(rel_path, content):
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")

print("Starting generation of complete EvoCare Knowledge Base...")

if os.path.exists(BASE_DIR):
    shutil.rmtree(BASE_DIR)

# ==============================================================================
# 1. ROOT SYSTEM DOCUMENTATION
# ==============================================================================

write_file("README.md", """# EvoCare Knowledge Base — Longitudinal Patient Memory System

> [!WARNING]
> **FABRICATED / SYNTHETIC DEMO PATIENT**: All clinical, caregiver, laboratory, and pharmacological data in this Knowledge Base are completely synthetic and created solely for demonstrating the EvoCare longitudinal memory architecture. No real patient data is used.

---

## 1. What is EvoCare?

**EvoCare** is an evolving, longitudinal memory system designed for elderly healthcare. 

In traditional medicine, clinical consultations operate as isolated episodic snapshots. An attending physician typically has only 10–15 minutes to evaluate an elderly patient and must rely on spot exams or fragmented recollections. Crucial day-to-day signals—such as gradual gait hesitation, subtle cognitive dips in the evening, transient dizziness upon standing, or fluctuating appetite—are lost between visits.

EvoCare solves this by establishing a continuously updated **Patient Knowledge Base (Patient Wiki)** that ingests raw evidence from multiple human and clinical sources, anchors them against an immutable baseline, tracks longitudinal trajectories, and highlights emerging risks and conflicts for clinicians.

```
RAW EVIDENCE (Doctor, Caregiver, Labs, Meds, Patient)
       ↓
STRUCTURED MEMORY & EVIDENCE ENGINE
       ↓
PATIENT WIKI (Clinical & Caregiver Subspaces)
       ↓
BASELINE ENGINE (Immutable Reference Anchors)
       ↓
TRENDS, PATTERNS & CONFLICT DETECTION
       ↓
EVOLVING PATIENT MEMORY SUMMARY
```

---

## 2. Why Caregiver Information Matters & Why It Must Stay Separate

Family caregivers are the continuous observers of an elderly individual's daily life. They witness functional changes weeks or months before a formal clinical encounter. However, caregiver reports present two unique challenges:
1. **Colloquial & Subjective**: Caregivers describe what they see (e.g., *"She was not herself"*, *"She held the table"*), which lacks diagnostic specificity.
2. **Risk of Misattribution**: Treating caregiver impressions as formal diagnoses can lead to premature labeling (e.g., mistaking acute evening confusion for permanent dementia, or treating a near-fall as a confirmed fall).

**EvoCare's Core Innovation**: Strict source separation. 
- **Doctor Information** represents formal diagnostic and clinical ground truth (`EV-DR-*`).
- **Caregiver Observations** represent real-world contextual behavioral and functional notes (`EV-CG-*`).
- **Laboratory Information** represents objective physiological biomarkers (`EV-LAB-*`).
- **AI-Derived Patterns** represent synthesized temporal trajectories with full provenance citation (`AI_DERIVED`).

These streams are never merged into an undifferentiated narrative.

---

## 3. How the Patient Wiki Works

The Knowledge Base is organized as an Obsidian-compatible Markdown vault structured into clear domains:
- **`Raw Evidence/`**: Immutable records of every encounter, lab, prescription, and caregiver observation.
- **`Patient Wiki/P001 Meenakshi Raman/`**:
  - **`Clinical/`**: Formal medical history, diagnoses, medications, physical exams, and lab panels.
  - **`Caregiver/`**: Topical logs tracking Mobility, Falls, Dizziness, Cognition, Nutrition, Sleep, Pain, Behavior, and Medication Adherence.
  - **`Derived/`**: Synthesized functional baselines, chronological trend trajectories, conflict matrices, and the high-level Patient Memory Summary.
- **`Demo/`**: 15 rigorous evaluation questions and evidence-grounded answers.

---

## 4. Evidence Provenance & Memory Rules

Every derived claim in the Wiki must cite its supporting Evidence IDs (e.g., `[[EV-DR-005]]`, `[[EV-CG-031]]`).
- **Baseline Preservation**: The historical baseline (`Derived/Baseline.md`) is never overwritten by acute fluctuations.
- **Near-Fall vs. Fall Distinction**: Catching a patient before floor contact is strictly a `NEAR_FALL` and never converted into a `FALL`.
- **Handling Ambiguity**: Incomplete statements (e.g., *"He is dizzy"*) preserve `UNKNOWN` fields rather than inventing synthetic vitals.
- **Doctor as Sole Decision-Maker**: EvoCare highlights patterns and frames clinical considerations, but never issues independent medical diagnoses.

---

## 5. Evolution to Future Phases

This repository represents **PHASE 1: The Knowledge Base**. It defines the core data model and semantic structure that future software layers will interact with:
- **PHASE 1 (Completed)**: Obsidian Knowledge Base Vault, Multi-Source Evidence Engine, Structured Patient Wiki, Baseline & Trend Modeling.
- **PHASE 2 (Future)**: Python / FastAPI Longitudinal Memory Core with bidirectional Markdown synchronization.
- **PHASE 3 (Future)**: Caregiver Multimodal Ingestion (Voice/STT, WhatsApp/Telegram bot) with interactive ambiguity resolution.
- **PHASE 4 (Future)**: Clinician Longitudinal Dashboard with Graph Exploration and Temporal Scrubbing.
- **PHASE 5 (Future)**: Clinical Reasoning Assistant and EHR Integration (FHIR/HL7).

---

## 6. Knowledge Base Status

- **Status**: COMPLETE
- **Patient**: P001 — Meenakshi Raman (78F, Chennai, Tamil Nadu)
- **Synthetic Evidence Records**: 65
  - **Caregiver Observations**: 47 records (`EV-CG-001` to `EV-CG-047`) across Aug–Sep 2026
  - **Doctor Records**: 5 records (`EV-DR-001` to `EV-DR-005`) across 2025-12 to 2026-08
  - **Medical Records**: 2 records (`EV-MR-001`, `EV-MR-002`)
  - **Patient Statements**: 4 records (`EV-PAT-001` to `EV-PAT-004`)
  - **Medication Records**: 4 active records (`EV-MED-001` to `EV-MED-004`)
  - **Lab Records**: 3 longitudinal panels (`EV-LAB-001` to `EV-LAB-003`)
- **Wiki Pages**: 24 core pages
- **Derived Trend Pages**: 7 dedicated trajectory analyses
- **Conflict Cases**: 3 documented multi-source differences
- **Ambiguous Cases**: 5 deliberately preserved incomplete observations
- **Obsidian Ready**: YES
""")

write_file("EvoCare Architecture.md", """# EvoCare Architecture

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
""")

write_file("Data Model.md", """# EvoCare Data Model

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

This document specifies the conceptual entities, data types, validation rules, and structural relationships within the EvoCare Knowledge Base.

---

## 1. Entity Relationship Overview

```
 [Patient] 1 ─────── ∞ [Evidence]
                         │
         ┌───────────────┼───────────────┬────────────────┐
         │               │               │                │
         v               v               v                v
  [Doctor Record]  [Caregiver Obs]  [Lab Record]    [Medication]
         │               │               │                │
         └───────────────┼───────────────┴────────────────┘
                         v
                [Patient Wiki Page]
                         │
                         v
             [Derived Claim / Trend]
                         │
                         v
              [Conflict / Ambiguity]
```

---

## 2. Core Entities

### 2.1 `Patient`
The primary human entity whose longitudinal health trajectory is tracked.
- `patient_id`: String (Unique, e.g., `P001`)
- `full_name`: String (e.g., `"Meenakshi Raman"`)
- `age`: Integer (e.g., `78`)
- `sex`: String (`Female` | `Male` | `Other`)
- `location`: String (e.g., `"Chennai, Tamil Nadu"`)
- `synthetic_flag`: Boolean (`True`)

### 2.2 `Evidence`
The atomic, immutable unit of information entering the system.
- `evidence_id`: String (Unique, e.g., `EV-CG-001`, `EV-DR-001`, `EV-LAB-001`)
- `patient_id`: String (`P001`)
- `source_type`: Enum (`DOCTOR` | `CAREGIVER` | `LAB_RECORD` | `MEDICATION_RECORD` | `PATIENT` | `MEDICAL_RECORD`)
- `source_id`: String (e.g., `CG001`, `DR_CHANDRAN`, `METROPOLIS_LABS`)
- `observed_at`: ISO Date / Timestamp (e.g., `2026-08-20`)
- `recorded_at`: ISO Date / Timestamp (e.g., `2026-08-20`)
- `original_statement`: String (Verbatim raw text or structured measurement)
- `status`: Enum (`IMMUTABLE`)

### 2.3 `Caregiver Observation`
Sub-entity of Evidence originating from family or formal caregivers.
- `domain`: Enum (`MOBILITY` | `COGNITION` | `NUTRITION` | `SLEEP` | `PAIN` | `DIZZINESS` | `FALLS` | `BEHAVIOR` | `MEDICATION_ADHERENCE`)
- `event_classification`: Enum (`NORMAL` | `UNSTEADY` | `NEAR_FALL` | `FALL` | `APPETITE_DECREASE` | `CONFUSION` | `PAIN_REPORT` | `UNKNOWN`)
- `completeness`: Enum (`COMPLETE` | `AMBIGUOUS_REQUIRES_CLARIFICATION`)
- `missing_fields`: Array of Strings (e.g., `["severity", "duration", "trigger"]`)

### 2.4 `Doctor Record`
Sub-entity of Evidence originating from clinical visits.
- `encounter_type`: Enum (`ROUTINE_CONSULTATION` | `FOLLOW_UP` | `EMERGENCY`)
- `clinician_name`: String (e.g., `"Dr. S. Chandran, MD"`)
- `diagnoses_addressed`: Array of Strings (e.g., `["Type 2 Diabetes", "Hypertension", "Hyperlipidemia", "Osteoarthritis"]`)
- `clinical_findings`: String (Documented physical and mental examination)
- `treatment_plan`: String (Medication adjustments, follow-up intervals)

### 2.5 `Lab Record`
Objective physiological biomarker panels.
- `test_panel`: String (e.g., `"Glycemic & Renal Function Panel"`)
- `biomarkers`: Key-Value Map (e.g., `HbA1c: 7.4%`, `Creatinine: 0.9 mg/dL`, `Sodium: 137 mmol/L`, `Potassium: 4.3 mmol/L`, `Hemoglobin: 12.1 g/dL`)

### 2.6 `Medication`
Active and historical pharmacological regimens.
- `medication_id`: String (`EV-MED-001`)
- `drug_name`: String (e.g., `"Metformin"`)
- `dose`: String (`500 mg`)
- `frequency`: String (`twice daily`)
- `status`: Enum (`ACTIVE` | `DISCONTINUED` | `PRN`)
- `indication`: String (e.g., `"Type 2 Diabetes Mellitus"`)

### 2.7 `Wiki Page`
A curated Markdown page compiling evidence into a structured topical view.
- `title`: String
- `section_structure`: Current State, Baseline, Clinical Information, Caregiver Observations, Historical Information, AI-Derived Pattern, Conflicts, Unknown / Missing Information, Evidence, Related Concepts.

### 2.8 `Derived Claim / Trend`
Synthesized longitudinal interpretation generated by LLM analysis.
- `claim_id`: String
- `domain`: String
- `temporal_trajectory`: Progression summary
- `supporting_evidence_ids`: Array of Strings (`["EV-DR-005", "EV-CG-031", "EV-CG-040"]`)
- `clinical_certainty`: Enum (`OBSERVATIONAL_PATTERN` | `HYPOTHESIS_FOR_MD`)

### 2.9 `Conflict`
A detected divergence between clinical documentation and caregiver observations.
- `conflict_id`: String (e.g., `CONF-001`)
- `domain`: String (e.g., `Mobility`)
- `doctor_view`: String (`"Independently mobile without walking aids"`)
- `doctor_evidence_id`: String (`EV-DR-005`)
- `caregiver_view`: String (`"Requires support for ambulation and had a near-fall"`)
- `caregiver_evidence_ids`: Array of Strings (`["EV-CG-021", "EV-CG-031", "EV-CG-036"]`)
- `status`: Enum (`CONFLICTING_REQUIRES_CLINICIAN_REVIEW`)
- `resolution_strategy`: DO NOT AUTO-RESOLVE. Flag for clinician evaluation.

---

## 3. Related References
- [[Source Types]]
- [[Memory Rules]]
- [[Patient Wiki/P001 Meenakshi Raman/Patient Overview|Patient Overview]]
""")

write_file("Source Types.md", """# EvoCare Source Types

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

EvoCare enforces strict source taxonomy. Every statement, metric, and summary in the Knowledge Base is tagged with its authoritative source type to prevent contamination between clinical facts, caregiver observations, and AI deductions.

---

## 1. Source Classification Hierarchy

```
+-------------------------------------------------------------------------------+
| SOURCE TYPE       | DESCRIPTION                      | AUTHORITY & NATURE     |
+-------------------+----------------------------------+------------------------+
| DOCTOR            | Formally documented clinical     | High Clinical Weight;  |
|                   | consultations by physicians      | Diagnostic Ground Truth|
+-------------------+----------------------------------+------------------------+
| CAREGIVER         | Daily behavioral, functional,    | High Contextual Weight;|
|                   | and symptom logs by family       | Non-Diagnostic Obs.    |
+-------------------+----------------------------------+------------------------+
| PATIENT           | Self-reported symptoms, baseline | Subjective Experience; |
|                   | statements, and historical notes | Personal Baseline      |
+-------------------+----------------------------------+------------------------+
| MEDICAL_RECORD    | Prior institutional charts,      | Historical Clinical    |
|                   | discharge summaries, past notes  | Reference              |
+-------------------+----------------------------------+------------------------+
| MEDICATION_RECORD | Active and historical pharmacy   | Pharmacological Truth  |
|                   | prescriptions and schedules      |                        |
+-------------------+----------------------------------+------------------------+
| LAB_RECORD        | Quantitative clinical pathology  | Objective Biomarker    |
|                   | laboratory reports               | Ground Truth           |
+-------------------+----------------------------------+------------------------+
| SYSTEM            | Automated ingest timestamps,     | Operational Metadata   |
|                   | audit records, schema checks     |                        |
+-------------------+----------------------------------+------------------------+
| AI_DERIVED        | Synthesized longitudinal trends, | Non-Diagnostic Insight;|
|                   | baseline deviations, summaries   | Must cite Evidence IDs |
+-------------------+----------------------------------+------------------------+
| AI_CLINICAL_      | Prompts and differential queries | Clinical Discussion    |
| CONSIDERATION     | prepared for physician review    | Flags Only             |
+-------------------------------------------------------------------------------+
```

---

## 2. In-Depth Source Definitions

### 1. `DOCTOR`
- **Definition**: Statements, diagnoses, physical exams, and treatment directives authored by a licensed medical practitioner during formal encounters.
- **Rule**: Doctor statements represent clinical diagnostic ground truth for conditions (e.g., Type 2 Diabetes, Knee Osteoarthritis).
- **Prefix**: `EV-DR-*`

### 2. `CAREGIVER`
- **Definition**: Observations reported by family members, live-in aids, or community caregivers.
- **Rule**: Caregiver observations provide essential real-world context (e.g., unsteadiness, appetite dips, bedtime routines). They are **never** treated as formal medical diagnoses.
- **Prefix**: `EV-CG-*` (e.g., `CG001` Daughter, `CG002` Son, `CG003` Family Caregiver)

### 3. `PATIENT`
- **Definition**: Direct verbatim statements from the patient regarding feelings, pain levels, preferences, and personal history.
- **Prefix**: `EV-PAT-*`

### 4. `MEDICAL_RECORD`
- **Definition**: Pre-existing medical summaries, hospital discharge summaries, or retrospective clinical dossiers.
- **Prefix**: `EV-MR-*`

### 5. `MEDICATION_RECORD`
- **Definition**: Prescribed drug regimens, dosages, frequencies, and administration routes.
- **Prefix**: `EV-MED-*`

### 6. `LAB_RECORD`
- **Definition**: Certified quantitative laboratory assays (blood, urine, imaging biomarkers).
- **Prefix**: `EV-LAB-*`

### 7. `AI_DERIVED`
- **Definition**: Computational synthesis across longitudinal evidence nodes (e.g., baseline delta, trend vectors).
- **Rule**: Must cite every supporting `EV-*` ID and must never hallucinate missing values or clinical diagnoses.

### 8. `AI_CLINICAL_CONSIDERATION`
- **Definition**: AI-generated exploratory prompts highlighting potential risks or questions for the attending physician during the next consultation.

---

## 3. Related References
- [[Data Model]]
- [[Memory Rules]]
- [[Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts|Derived Conflicts]]
""")

write_file("Memory Rules.md", """# EvoCare Memory Rules & Invariants

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

The EvoCare Knowledge Base adheres to 14 inviolable memory rules designed to preserve data integrity, clinical safety, and longitudinal continuity.

---

## The 14 Inviolable Memory Rules

### 1. Raw Evidence is Immutable
Once written to `Raw Evidence/`, an evidence document (`EV-*`) can never be modified, truncated, or deleted. All updates arrive as new evidence records.

### 2. Historical Information is Never Silently Overwritten
New observations do not delete or overwrite past observations. Both the historical state and the current state remain simultaneously queryable.

### 3. Every Derived Claim Requires Explicit Evidence Citation
Any assertion made in a `Derived/` or `Patient Wiki/` page must cite the specific Evidence IDs (`[[EV-DR-001]]`, `[[EV-CG-031]]`, etc.) supporting it. Ungrounded generation is strictly prohibited.

### 4. Source Types Must Remain Strictly Separated
Clinical facts from physicians, contextual observations from caregivers, and quantitative values from laboratories must occupy distinct sections and metadata schemas.

### 5. Caregiver Observations are Not Diagnoses
Caregiver statements describe what was witnessed (e.g., *"She was confused"*, *"She ate less"*). They are never converted into medical diagnoses (e.g., *"Patient has Alzheimer's Disease"*, *"Patient has Malnutrition"*).

### 6. AI-Derived Patterns are Not Clinician-Confirmed Facts
AI synthesis represents observational trend analysis (e.g., *"Possible deviation from mobility baseline"*). They are designated as hypotheses for clinician review.

### 7. Unknown Information Remains Unknown
When a caregiver's report lacks critical clinical parameters (e.g., *"He is dizzy"* without duration or trigger), the system marks fields as `UNKNOWN` / `REQUIRES CLARIFICATION` rather than inventing synthetic defaults.

### 8. Conflicts are Preserved, Not Reconciled by Elimination
When a physician documents *"Independently mobile"* while a caregiver reports *"Required walking support"*, the system documents both in `Derived/Conflicts.md` and flags the case for clinician adjudication.

### 9. Temporal Context Matters
The clinical meaning of an observation depends on its timing relative to medications, meals, prior baseline, and preceding events (e.g., morning vs. evening unsteadiness).

### 10. Latest Information Does Not Automatically Erase Historical Baseline
An acute change (e.g., 5 days of walking unsteadiness) does not overwrite the established long-term baseline (`Derived/Baseline.md`). It is modeled as a delta against the baseline.

### 11. Improvements Must Be Faithfully Recorded
Longitudinal tracking captures positive trajectories and recovery (e.g., 2026-09-09: *"Walking better today without support"*) alongside declines.

### 12. Near-Fall and Fall are Distinct Clinical Entities
A near-fall where a caregiver catches the patient before floor contact is classified as `NEAR_FALL`. It must **never** be counted as a completed `FALL`.

### 13. AI Cannot Invent Missing Information
If vital parameters (blood pressure during dizziness, duration of confusion) are unrecorded, the AI must explicitly identify them as gaps.

### 14. Doctor Remains the Sole Final Decision-Maker
The Knowledge Base exists to augment and contextualize clinical judgment, never to automate treatment decisions or issue independent diagnoses.

---

## Related References
- [[Data Model]]
- [[Source Types]]
- [[EvoCare Architecture]]
""")

write_file("Timeline.md", """# Longitudinal Patient Timeline: P001 Meenakshi Raman

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Patient: [[Patient Wiki/P001 Meenakshi Raman/Patient Overview|Meenakshi Raman (P001)]] | Age: 78 | Sex: Female | Location: Chennai, TN

This chronological timeline compiles events across all sources: **Clinical Encounters**, **Caregiver Observations**, **Laboratory Biomarkers**, **Medications**, and **Derived Milestones**.

---

## 1. Timeline Chronology

```
2025-12-15 ─── [CLINICAL] Routine Review: T2DM, HTN, Hyperlipidemia, Knee OA; Stable, Independent (EV-DR-001)
2026-01-10 ─── [PATIENT/MR] Historical Fall ~8 months prior; no acute fracture or hospitalization (EV-PAT-001, EV-MR-002)
2026-02-10 ─── [LAB] Glycemic & Renal Panel: HbA1c 7.1%, Cr 0.9 mg/dL, Na 138, K 4.3, Hb 12.4 (EV-LAB-001)
2026-02-18 ─── [CLINICAL] Follow-up: Chronic conditions stable; independent mobility; no falls (EV-DR-002)
2026-04-12 ─── [CLINICAL] Routine Follow-up: Stable; occasional forgetfulness; independent mobility (EV-DR-003)
2026-05-12 ─── [LAB] Glycemic & Renal Panel: HbA1c 7.3%, Cr 0.9 mg/dL, Na 139, K 4.2, Hb 12.2 (EV-LAB-002)
2026-06-14 ─── [CLINICAL] Follow-up: Independent walking continues; occasional knee discomfort (EV-DR-004)
2026-08-15 ─── [LAB] Glycemic & Renal Panel: HbA1c 7.4%, Cr 0.9 mg/dL, Na 137, K 4.3, Hb 12.1 (EV-LAB-003)
2026-08-18 ─── [CLINICAL] Routine Review: Ambulates independently; no acute neurological signs; family assists meds (EV-DR-005)
2026-08-20 ─── [CAREGIVER] Walking around house normally (CG001 / EV-CG-001)
2026-08-21 ─── [CAREGIVER] Forgot where she kept her glasses (CG001 / EV-CG-002)
2026-08-22 ─── [CAREGIVER] Finished most of lunch (CG002 / EV-CG-003)
2026-08-22 ─── [CAREGIVER] Good mood, talked with family (CG002 / EV-CG-004)
2026-08-23 ─── [CAREGIVER] Slept around 7 hours (CG001 / EV-CG-005)
2026-08-23 ─── [CAREGIVER] Ambiguous note: "He is dizzy" [UNKNOWN severity/duration] (CG003 / EV-CG-043)
2026-08-24 ─── [CAREGIVER] Slightly unsteady when getting up from chair (CG003 / EV-CG-006)
2026-08-24 ─── [CAREGIVER] Knees hurt a little after walking (CG003 / EV-CG-007)
2026-08-25 ─── [CAREGIVER] Said she felt dizzy for a little while [UNKNOWN cause/severity] (CG001 / EV-CG-008)
2026-08-25 ─── [CAREGIVER] Ambiguous note: "She is weak today" [UNKNOWN metrics] (CG003 / EV-CG-044)
2026-08-26 ─── [CAREGIVER] Morning medicines taken with help (CG001 / EV-CG-009)
2026-08-26 ─── [CAREGIVER] Dizziness follow-up: severity not sure, duration unknown, no fall (CG001 / EV-CG-010)
2026-08-27 ─── [CAREGIVER] Holding dining table for support while walking (CG002 / EV-CG-011)
2026-08-28 ─── [CAREGIVER] Left about half of lunch (CG003 / EV-CG-012)
2026-08-28 ─── [CAREGIVER] Ambiguous note: "She is confused" [UNKNOWN domain/trigger] (CG002 / EV-CG-045)
2026-08-29 ─── [CAREGIVER] Asked same question twice in evening (CG001 / EV-CG-013)
2026-08-30 ─── [CAREGIVER] Walked normally in the morning (CG002 / EV-CG-014)
2026-08-30 ─── [CAREGIVER] Knee pain mild (CG002 / EV-CG-015)
2026-08-30 ─── [CAREGIVER] Quiet in the afternoon (CG001 / EV-CG-016)
2026-08-31 ─── [CAREGIVER] Woke up three times last night (CG001 / EV-CG-017)
2026-08-31 ─── [CAREGIVER] Ambiguous note: "She didn't eat much" [UNKNOWN portion/meal] (CG003 / EV-CG-046)
2026-09-01 ─── [CAREGIVER] Dizziness after getting out of bed, resolved after sitting (CG003 / EV-CG-018)
2026-09-01 ─── [CAREGIVER] Ate less than usual at dinner (CG001 / EV-CG-019)
2026-09-01 ─── [CAREGIVER] Almost forgot evening medicine; reminded (CG001 / EV-CG-020)
2026-09-02 ─── [CAREGIVER] Needed someone's arm while walking outside (CG002 / EV-CG-021)
2026-09-02 ─── [CAREGIVER] Seemed confused about what day it was (CG002 / EV-CG-022)
2026-09-03 ─── [CAREGIVER] Only had a few bites of dinner (CG001 / EV-CG-023)
2026-09-03 ─── [CAREGIVER] Slept poorly (CG001 / EV-CG-024)
2026-09-03 ─── [CAREGIVER] Ambiguous note: "She was not herself" [UNKNOWN detail] (CG001 / EV-CG-047)
2026-09-04 ─── [CAREGIVER] Slower than usual while walking (CG003 / EV-CG-025)
2026-09-04 ─── [CAREGIVER] Completely normal and chatting in morning (CG001 / EV-CG-026)
2026-09-04 ─── [CAREGIVER] Did not complain about knee pain today (CG003 / EV-CG-027)
2026-09-05 ─── [CAREGIVER] Complained of dizziness again in evening (CG001 / EV-CG-028)
2026-09-05 ─── [CAREGIVER] Appetite seemed better today (CG001 / EV-CG-029)
2026-09-05 ─── [CAREGIVER] Laughing and watching television with everyone (CG002 / EV-CG-030)
2026-09-06 ─── [CAREGIVER] NEAR_FALL: Almost fell near bathroom, caught by caregiver (CG003 / EV-CG-031)
2026-09-06 ─── [CAREGIVER] Felt dizzy and held wall for a few seconds (CG003 / EV-CG-032)
2026-09-06 ─── [CAREGIVER] Organized medicines for the week (CG001 / EV-CG-033)
2026-09-07 ─── [CAREGIVER] Confused again around dinner time (CG002 / EV-CG-034)
2026-09-07 ─── [CAREGIVER] Slept better (CG001 / EV-CG-035)
2026-09-08 ─── [CAREGIVER] Needed support to walk from bedroom to kitchen (CG001 / EV-CG-036)
2026-09-08 ─── [CAREGIVER] Ate about three quarters of meal (CG001 / EV-CG-037)
2026-09-08 ─── [CAREGIVER] Knees hurt after going outside (CG002 / EV-CG-038)
2026-09-08 ─── [CAREGIVER] Frustrated because walking slowly (CG001 / EV-CG-039)
2026-09-09 ─── [CAREGIVER] Walking better today; did not need support inside house (CG001 / EV-CG-040)
2026-09-09 ─── [CAREGIVER] Recognized everyone and was talking normally (CG001 / EV-CG-041)
2026-09-09 ─── [CAREGIVER] Took medicines on time today (CG002 / EV-CG-042)
```

---

## 2. Longitudinal Domain Summary Links
- **Mobility**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Mobility Trends|Mobility Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Mobility|Caregiver Mobility Log]]
- **Cognition**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Cognition Trends|Cognition Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Cognition|Caregiver Cognition Log]]
- **Nutrition**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Nutrition Trends|Nutrition Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Nutrition|Caregiver Nutrition Log]]
- **Sleep**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Sleep Trends|Sleep Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Sleep|Caregiver Sleep Log]]
- **Dizziness**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Dizziness Trends|Dizziness Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Dizziness|Caregiver Dizziness Log]]
- **Falls / Near-Falls**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Falls Trends|Falls Trends]] & [[Patient Wiki/P001 Meenakshi Raman/Caregiver/Falls|Caregiver Falls Log]]
- **Conflicts Matrix**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts|Derived Conflicts]]
- **Executive Memory Summary**: [[Patient Wiki/P001 Meenakshi Raman/Derived/Patient Memory Summary|Patient Memory Summary]]
""")

# ==============================================================================
# 2. RAW EVIDENCE FILES
# ==============================================================================

# Patient self-reports
write_file("Raw Evidence/Patient/EV-PAT-001.md", """# Evidence EV-PAT-001

Patient ID: P001
Source Type: PATIENT
Source ID: PAT001
Observed At: 2026-01-10
Recorded At: 2026-01-10
Original Statement:
"I slipped on the wet tile floor about 8 months ago, but my family helped me up right away and I was not badly hurt."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Patient/EV-PAT-002.md", """# Evidence EV-PAT-002

Patient ID: P001
Source Type: PATIENT
Source ID: PAT001
Observed At: 2026-08-01
Recorded At: 2026-08-01
Original Statement:
"I usually walk around the house without any walking stick or support. I manage all my daily routine myself."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Patient/EV-PAT-003.md", """# Evidence EV-PAT-003

Patient ID: P001
Source Type: PATIENT
Source ID: PAT001
Observed At: 2026-08-01
Recorded At: 2026-08-01
Original Statement:
"My appetite is normally good. I enjoy home-cooked South Indian vegetarian food and finish my meals."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Patient/EV-PAT-004.md", """# Evidence EV-PAT-004

Patient ID: P001
Source Type: PATIENT
Source ID: PAT001
Observed At: 2026-08-01
Recorded At: 2026-08-01
Original Statement:
"Sometimes I misplace my reading glasses or forget where I placed keys, but I know all my children and grandchildren very well."
Status: IMMUTABLE
""")

# Medical Records
write_file("Raw Evidence/Medical Records/EV-MR-001.md", """# Evidence EV-MR-001

Patient ID: P001
Source Type: MEDICAL_RECORD
Source ID: APOLLO_CHENNAI_EHR
Observed At: 2025-10-01
Recorded At: 2025-10-01
Original Statement:
"Longitudinal summary: 77-year-old female with long-standing Type 2 Diabetes Mellitus (diagnosed 2014), Essential Hypertension (diagnosed 2016), Hyperlipidemia, and bilateral Knee Osteoarthritis (Grade II Kellgren-Lawrence). No history of stroke, myocardial infarction, or diagnosed dementia."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Medical Records/EV-MR-002.md", """# Evidence EV-MR-002

Patient ID: P001
Source Type: MEDICAL_RECORD
Source ID: APOLLO_CHENNAI_EHR
Observed At: 2026-01-12
Recorded At: 2026-01-12
Original Statement:
"Outpatient chart note: Patient reported an accidental slip and fall at home approximately two days prior. Examination revealed mild left gluteal contusion, full range of motion of bilateral hips and knees, no bony tenderness, no radiographic evidence of fracture. Ambulating independently without assistive device."
Status: IMMUTABLE
""")

# Doctor consultations
write_file("Raw Evidence/Doctor/EV-DR-001.md", """# Evidence EV-DR-001

Patient ID: P001
Source Type: DOCTOR
Source ID: DR_CHANDRAN
Observed At: 2025-12-15
Recorded At: 2025-12-15
Original Statement:
"Routine geriatric clinical review. Patient presents for chronic disease management. Assessed for Type 2 Diabetes Mellitus, Hypertension, Hyperlipidemia, and bilateral Knee Osteoarthritis. Chronic conditions are generally stable. Physical examination reveals independent mobility and steady gait without assistive devices. Patient mentions occasional benign forgetfulness. No acute neurological concerns documented. Plan: Continue current pharmacological therapy."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Doctor/EV-DR-002.md", """# Evidence EV-DR-002

Patient ID: P001
Source Type: DOCTOR
Source ID: DR_CHANDRAN
Observed At: 2026-02-18
Recorded At: 2026-02-18
Original Statement:
"Bimonthly follow-up visit. Chronic medical conditions remain reasonably stable. Diabetes monitoring continued with recent HbA1c 7.1%. Bilateral knee joint discomfort is intermittent and managed with PRN paracetamol. Ambulation remains fully independent. No recent falls reported since the minor slip in January. Continue Metformin 500mg BID, Amlodipine 5mg OD, Atorvastatin 10mg ON."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Doctor/EV-DR-003.md", """# Evidence EV-DR-003

Patient ID: P001
Source Type: DOCTOR
Source ID: DR_CHANDRAN
Observed At: 2026-04-12
Recorded At: 2026-04-12
Original Statement:
"Routine clinical follow-up. Vital signs: BP 132/82 mmHg, Pulse 74 bpm. Chronic conditions stable. Patient remains independently mobile around her residence and community. Occasional benign forgetfulness reported by patient, but orientation to time, place, and person intact. No major functional decline documented. Maintain existing therapeutic regimen."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Doctor/EV-DR-004.md", """# Evidence EV-DR-004

Patient ID: P001
Source Type: DOCTOR
Source ID: DR_CHANDRAN
Observed At: 2026-06-14
Recorded At: 2026-06-14
Original Statement:
"Follow-up examination. Independent walking continues without aids. Occasional knee discomfort noted after prolonged standing. Cardiovascular and respiratory exams unremarkable. No recent falls reported by patient or accompanying family. Continue current management plan."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Doctor/EV-DR-005.md", """# Evidence EV-DR-005

Patient ID: P001
Source Type: DOCTOR
Source ID: DR_CHANDRAN
Observed At: 2026-08-18
Recorded At: 2026-08-18
Original Statement:
"Routine clinical review. Patient ambulates independently into consultation room with steady pace. No acute focal neurological deficits or acute symptoms documented. Family notes they assist with weekly pillbox organization. Glycemic control stable (HbA1c 7.4%). Plan: Continue current medication regimen without alteration. Next routine review in 2 months."
Status: IMMUTABLE
""")

# Medications
write_file("Raw Evidence/Medications/EV-MED-001.md", """# Evidence EV-MED-001

Patient ID: P001
Source Type: MEDICATION_RECORD
Source ID: DR_CHANDRAN_RX
Observed At: 2025-12-15
Recorded At: 2025-12-15
Original Statement:
"Metformin hydrochloride 500 mg oral tablet. Frequency: twice daily with meals (morning and evening). Indication: Type 2 Diabetes Mellitus. Status: ACTIVE."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Medications/EV-MED-002.md", """# Evidence EV-MED-002

Patient ID: P001
Source Type: MEDICATION_RECORD
Source ID: DR_CHANDRAN_RX
Observed At: 2025-12-15
Recorded At: 2025-12-15
Original Statement:
"Amlodipine besylate 5 mg oral tablet. Frequency: once daily in the morning. Indication: Essential Hypertension. Status: ACTIVE."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Medications/EV-MED-003.md", """# Evidence EV-MED-003

Patient ID: P001
Source Type: MEDICATION_RECORD
Source ID: DR_CHANDRAN_RX
Observed At: 2025-12-15
Recorded At: 2025-12-15
Original Statement:
"Atorvastatin calcium 10 mg oral tablet. Frequency: once nightly at bedtime. Indication: Hyperlipidemia / Cardiovascular risk reduction. Status: ACTIVE."
Status: IMMUTABLE
""")

write_file("Raw Evidence/Medications/EV-MED-004.md", """# Evidence EV-MED-004

Patient ID: P001
Source Type: MEDICATION_RECORD
Source ID: DR_CHANDRAN_RX
Observed At: 2025-12-15
Recorded At: 2025-12-15
Original Statement:
"Paracetamol 500 mg oral tablet. Frequency: PRN (as needed), maximum 2000 mg/24hr. Context: Occasional bilateral knee discomfort related to osteoarthritis. Status: ACTIVE."
Status: IMMUTABLE
""")

# Labs
write_file("Raw Evidence/Labs/EV-LAB-001.md", """# Evidence EV-LAB-001

Patient ID: P001
Source Type: LAB_RECORD
Source ID: METROPOLIS_HEALTHCARE_CHENNAI
Observed At: 2026-02-10
Recorded At: 2026-02-10
Original Statement:
"Laboratory Panel:
- HbA1c: 7.1% (Reference: < 5.7% normal, < 7.5% geriatric target)
- Serum Creatinine: 0.9 mg/dL (Reference: 0.5 - 1.1 mg/dL)
- Serum Sodium: 138 mmol/L (Reference: 135 - 145 mmol/L)
- Serum Potassium: 4.3 mmol/L (Reference: 3.5 - 5.0 mmol/L)
- Hemoglobin: 12.4 g/dL (Reference: 12.0 - 15.5 g/dL)"
Status: IMMUTABLE
""")

write_file("Raw Evidence/Labs/EV-LAB-002.md", """# Evidence EV-LAB-002

Patient ID: P001
Source Type: LAB_RECORD
Source ID: METROPOLIS_HEALTHCARE_CHENNAI
Observed At: 2026-05-12
Recorded At: 2026-05-12
Original Statement:
"Laboratory Panel:
- HbA1c: 7.3% (Reference: < 5.7% normal, < 7.5% geriatric target)
- Serum Creatinine: 0.9 mg/dL (Reference: 0.5 - 1.1 mg/dL)
- Serum Sodium: 139 mmol/L (Reference: 135 - 145 mmol/L)
- Serum Potassium: 4.2 mmol/L (Reference: 3.5 - 5.0 mmol/L)
- Hemoglobin: 12.2 g/dL (Reference: 12.0 - 15.5 g/dL)"
Status: IMMUTABLE
""")

write_file("Raw Evidence/Labs/EV-LAB-003.md", """# Evidence EV-LAB-003

Patient ID: P001
Source Type: LAB_RECORD
Source ID: METROPOLIS_HEALTHCARE_CHENNAI
Observed At: 2026-08-15
Recorded At: 2026-08-15
Original Statement:
"Laboratory Panel:
- HbA1c: 7.4% (Reference: < 5.7% normal, < 7.5% geriatric target)
- Serum Creatinine: 0.9 mg/dL (Reference: 0.5 - 1.1 mg/dL)
- Serum Sodium: 137 mmol/L (Reference: 135 - 145 mmol/L)
- Serum Potassium: 4.3 mmol/L (Reference: 3.5 - 5.0 mmol/L)
- Hemoglobin: 12.1 g/dL (Reference: 12.0 - 15.5 g/dL)"
Status: IMMUTABLE
""")

# Caregiver Observations (47 records)
cg_data = [
    # Main timeline items
    ("EV-CG-001", "CG001", "2026-08-20", "She is walking around the house normally."),
    ("EV-CG-002", "CG001", "2026-08-21", "She forgot where she kept her glasses."),
    ("EV-CG-003", "CG002", "2026-08-22", "She finished most of her lunch."),
    ("EV-CG-004", "CG002", "2026-08-22", "She was in a good mood and talked with the family."),
    ("EV-CG-005", "CG001", "2026-08-23", "Slept around 7 hours."),
    ("EV-CG-006", "CG003", "2026-08-24", "She seemed slightly unsteady when getting up from the chair."),
    ("EV-CG-007", "CG003", "2026-08-24", "Her knees hurt a little after walking."),
    ("EV-CG-008", "CG001", "2026-08-25", "She said she felt dizzy for a little while."),
    ("EV-CG-009", "CG001", "2026-08-26", "She took her morning medicines with my help."),
    ("EV-CG-010", "CG001", "2026-08-26", "Follow-up regarding dizziness: severity not sure, duration unknown, no known fall occurred."),
    ("EV-CG-011", "CG002", "2026-08-27", "She was holding the dining table for support while walking."),
    ("EV-CG-012", "CG003", "2026-08-28", "She left about half of her lunch."),
    ("EV-CG-013", "CG001", "2026-08-29", "She asked the same question twice in the evening."),
    ("EV-CG-014", "CG002", "2026-08-30", "She walked normally in the morning."),
    ("EV-CG-015", "CG002", "2026-08-30", "She said her knee pain was mild."),
    ("EV-CG-016", "CG001", "2026-08-30", "She was quiet in the afternoon."),
    ("EV-CG-017", "CG001", "2026-08-31", "She woke up three times last night."),
    ("EV-CG-018", "CG003", "2026-09-01", "She felt dizzy after getting out of bed but it went away after sitting down."),
    ("EV-CG-019", "CG001", "2026-09-01", "She ate less than usual at dinner."),
    ("EV-CG-020", "CG001", "2026-09-01", "She almost forgot her evening medicine, so I reminded her."),
    ("EV-CG-021", "CG002", "2026-09-02", "She needed someone's arm while walking outside."),
    ("EV-CG-022", "CG002", "2026-09-02", "She seemed confused about what day it was."),
    ("EV-CG-023", "CG001", "2026-09-03", "She only had a few bites of dinner."),
    ("EV-CG-024", "CG001", "2026-09-03", "She slept poorly."),
    ("EV-CG-025", "CG003", "2026-09-04", "She was slower than usual while walking."),
    ("EV-CG-026", "CG001", "2026-09-04", "She was completely normal and chatting with us in the morning."),
    ("EV-CG-027", "CG003", "2026-09-04", "She did not complain about knee pain today."),
    ("EV-CG-028", "CG001", "2026-09-05", "She complained of dizziness again in the evening."),
    ("EV-CG-029", "CG001", "2026-09-05", "Her appetite seemed better today."),
    ("EV-CG-030", "CG002", "2026-09-05", "She was laughing and watching television with everyone."),
    ("EV-CG-031", "CG003", "2026-09-06", "She almost fell near the bathroom but I caught her."),
    ("EV-CG-032", "CG003", "2026-09-06", "She felt dizzy and held the wall for a few seconds."),
    ("EV-CG-033", "CG001", "2026-09-06", "I organized her medicines for the week."),
    ("EV-CG-034", "CG002", "2026-09-07", "She became confused again around dinner time."),
    ("EV-CG-035", "CG001", "2026-09-07", "She slept better."),
    ("EV-CG-036", "CG001", "2026-09-08", "She needed support to walk from the bedroom to the kitchen."),
    ("EV-CG-037", "CG001", "2026-09-08", "She ate about three quarters of her meal."),
    ("EV-CG-038", "CG002", "2026-09-08", "She said her knees hurt after going outside."),
    ("EV-CG-039", "CG001", "2026-09-08", "She seemed frustrated because she was walking slowly."),
    ("EV-CG-040", "CG001", "2026-09-09", "She was walking better today and did not need support inside the house."),
    ("EV-CG-041", "CG001", "2026-09-09", "She recognized everyone and was talking normally."),
    ("EV-CG-042", "CG002", "2026-09-09", "She took her medicines on time today."),
    # Ambiguous observations
    ("EV-CG-043", "CG003", "2026-08-23", "He is dizzy."),
    ("EV-CG-044", "CG003", "2026-08-25", "She is weak today."),
    ("EV-CG-045", "CG002", "2026-08-28", "She is confused."),
    ("EV-CG-046", "CG003", "2026-08-31", "She didn't eat much."),
    ("EV-CG-047", "CG001", "2026-09-03", "She was not herself."),
]

for ev_id, cg_id, dt, stmt in cg_data:
    content = f"""# Evidence {ev_id}

Patient ID: P001
Source Type: CAREGIVER
Source ID: {cg_id}
Observed At: {dt}
Recorded At: {dt}
Original Statement:
"{stmt}"
Status: IMMUTABLE
"""
    write_file(f"Raw Evidence/Caregiver/{ev_id}.md", content)

print("Raw evidence files written successfully.")

# ==============================================================================
# 3. PATIENT WIKI - CLINICAL SUBSPACE
# ==============================================================================

PATIENT_OVERVIEW_CONTENT = """# Patient Overview: Meenakshi Raman (P001)

> [!WARNING]
> **FABRICATED / SYNTHETIC DEMO PATIENT**: All details presented on this page represent synthetic data generated for demonstrating the EvoCare longitudinal memory architecture.

---

## 1. Demographics & Profile
- **Patient ID**: `P001`
- **Name**: Meenakshi Raman
- **Age**: 78
- **Sex**: Female
- **Location**: Chennai, Tamil Nadu
- **Primary Clinician**: Dr. S. Chandran, MD ([[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]])
- **Caregiver Network**:
  - `CG001`: Daughter
  - `CG002`: Son
  - `CG003`: Family Caregiver

---

## 2. Clinician-Confirmed Diagnoses
All diagnoses are documented by attending physicians:
1. **Type 2 Diabetes Mellitus** (Diagnosed 2014, Glycemic control stable, HbA1c 7.4% on 2026-08-15) — [[Clinical/Diagnoses|Diagnoses]]
2. **Essential Hypertension** (BP maintained at ~132/82 mmHg) — [[Clinical/Diagnoses|Diagnoses]]
3. **Hyperlipidemia** (Managed with statin therapy) — [[Clinical/Diagnoses|Diagnoses]]
4. **Bilateral Knee Osteoarthritis** (Grade II Kellgren-Lawrence, causes intermittent knee discomfort) — [[Clinical/Diagnoses|Diagnoses]]
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Medical Records/EV-MR-001|EV-MR-001]]*

---

## 3. Active Medications
- **Metformin 500 mg** — Twice daily with meals (Diabetes) — [[Raw Evidence/Medications/EV-MED-001|EV-MED-001]]
- **Amlodipine 5 mg** — Once daily in morning (Hypertension) — [[Raw Evidence/Medications/EV-MED-002|EV-MED-002]]
- **Atorvastatin 10 mg** — Once nightly at bedtime (Lipids) — [[Raw Evidence/Medications/EV-MED-003|EV-MED-003]]
- **Paracetamol 500 mg** — PRN (as needed) for knee discomfort — [[Raw Evidence/Medications/EV-MED-004|EV-MED-004]]
*Detailed Regimen: [[Clinical/Medications|Medications]]*

---

## 4. Documented Functional Baseline
The established long-term baseline remains active as the reference anchor:
- **Mobility**: Independently mobile, walks around home without walking aids.
- **Nutrition**: Good appetite, regularly completes meals.
- **Sleep**: Habitual ~7 hours per night with occasional waking.
- **Cognition**: Mild occasional forgetfulness; fully oriented to family and environment; **no dementia diagnosis**.
- **Pain**: Intermittent mild bilateral knee discomfort.
- **Dizziness**: No established persistent baseline pattern.
- **Falls History**: One historical slip ~8 months ago (Jan 2026) with no major injury or fracture.
*Detailed Baseline: [[Derived/Baseline|Baseline]]*

---

## 5. Recent Caregiver-Reported Observations (Aug–Sep 2026)
- **Mobility Changes**: Progressive unsteadiness observed between 2026-08-24 and 2026-09-08 (holding furniture, requiring arm support, slower pace), culminating in a **near-fall** on 2026-09-06 where caregiver caught her. Significant recovery noted on 2026-09-09 (walking better inside without support).
- **Dizziness**: Intermittent episodes upon rising and in evenings (2026-08-25, 2026-09-01, 2026-09-05, 2026-09-06).
- **Nutrition**: Temporary appetite dip with reduced meal intake (2026-08-28 to 2026-09-03) followed by recovery (2026-09-05, 2026-09-08).
- **Cognition**: Transient evening confusion notes (2026-08-29, 2026-09-02, 2026-09-07), interspersed with completely clear mornings (2026-09-04, 2026-09-09).

---

## 6. Current AI-Derived Patterns
- **Mobility Deviation**: Recent caregiver logs suggest a transient functional deviation from the independent baseline, followed by partial domestic recovery on 2026-09-09. ([[Derived/Mobility Trends|Mobility Trends]])
- **Dizziness Trajectory**: Recurrent episodic dizziness without established etiology; orthostatic/postural component suspected on 2026-09-01. ([[Derived/Dizziness Trends|Dizziness Trends]])
- **Cognitive Profile**: Intermittent evening confusion notes with preserved baseline recognition and morning clarity. Non-diagnostic. ([[Derived/Cognition Trends|Cognition Trends]])

---

## 7. Known Multi-Source Conflicts & Differences
1. **Mobility Status**: Doctor notes independent mobility ([[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]), whereas caregiver logs show recent assistance needs and a near-fall ([[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]). Flagged for clinician review.
2. **Fall vs. Near-Fall**: Historical chart reports no recent falls, which is clinically accurate because the 2026-09-06 event is classified strictly as `NEAR_FALL`.
3. **Appetite**: Stable chronic nutritional status in clinic vs. transient multi-day dietary dip observed by family.
*Detailed Analysis: [[Derived/Conflicts|Conflicts]]*

---

## 8. Unknown / Incomplete Information
- Exact duration and blood pressure correlation during dizziness episodes (`UNKNOWN`).
- Specific environmental or biomechanical triggers during the 2026-09-06 bathroom near-fall (`UNKNOWN`).
- Formal cognitive screening scores (e.g., MMSE/MoCA not documented in records).

---

## 9. Wiki Navigation & Core Links
- **Clinical Subspace**: [[Clinical/Medical History|Medical History]] | [[Clinical/Diagnoses|Diagnoses]] | [[Clinical/Medications|Medications]] | [[Clinical/Doctor Assessments|Doctor Assessments]] | [[Clinical/Laboratory History|Laboratory History]]
- **Caregiver Subspace**: [[Caregiver/Mobility|Mobility]] | [[Caregiver/Falls|Falls]] | [[Caregiver/Dizziness|Dizziness]] | [[Caregiver/Cognition|Cognition]] | [[Caregiver/Nutrition|Nutrition]] | [[Caregiver/Sleep|Sleep]] | [[Caregiver/Pain|Pain]] | [[Caregiver/Behavior|Behavior]] | [[Caregiver/Medication Adherence|Medication Adherence]]
- **Derived Subspace**: [[Derived/Baseline|Baseline]] | [[Derived/Mobility Trends|Mobility Trends]] | [[Derived/Cognition Trends|Cognition Trends]] | [[Derived/Nutrition Trends|Nutrition Trends]] | [[Derived/Sleep Trends|Sleep Trends]] | [[Derived/Dizziness Trends|Dizziness Trends]] | [[Derived/Falls Trends|Falls Trends]] | [[Derived/Conflicts|Conflicts]] | [[Derived/Patient Memory Summary|Patient Memory Summary]]
- **Evaluation & Demo**: [[Demo/Demo Questions|Demo Questions]] | [[Demo/Expected Answers|Expected Answers]] | [[Timeline]]
"""

write_file("Patient Wiki/P001 Meenakshi Raman/Patient Overview.md", PATIENT_OVERVIEW_CONTENT)

write_file("Patient Wiki/P001 Meenakshi Raman/Clinical/Medical History.md", """# Medical History: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## Current State
Patient is a 78-year-old female residing in Chennai, Tamil Nadu with a history of managed chronic metabolic, cardiovascular, and musculoskeletal conditions.

---

## Baseline
- Chronic conditions managed in outpatient setting for over a decade.
- Independently functional in activities of daily living (ADLs).
- No historical stroke, transient ischemic attack (TIA), coronary artery disease, or clinician-diagnosed neurocognitive disorder.

---

## Clinical Information (Doctor-Confirmed)
- **Type 2 Diabetes Mellitus**: Diagnosed ~2014. Managed on oral hypoglycemic agent (Metformin).
- **Essential Hypertension**: Diagnosed ~2016. Managed on calcium channel blocker (Amlodipine).
- **Hyperlipidemia**: Managed on statin therapy (Atorvastatin).
- **Bilateral Knee Osteoarthritis**: Kellgren-Lawrence Grade II changes; causes exertional knee discomfort managed with PRN analgesics.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]], [[Raw Evidence/Medical Records/EV-MR-001|EV-MR-001]]*

---

## Caregiver Observations
Caregiver reports family history support and confirms patient has managed her chronic conditions with family assistance for scheduling and grocery management.
*Evidence Reference: [[Raw Evidence/Caregiver/EV-CG-033|EV-CG-033]]*

---

## Historical Information
- Historical accidental slip at home in January 2026 (approximately 8 months prior to recent observation period). No fracture or hospitalization occurred.
*Evidence Reference: [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]], [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]*

---

## AI-Derived Pattern
The patient has a stable chronic disease profile with zero recorded hospitalizations or acute decompensations over the past 12 months.

---

## Conflicts
None. Medical history is consistent across clinical encounters.

---

## Unknown / Missing Information
- Exact year of knee osteoarthritis radiographic staging.

---

## Evidence
- [[Raw Evidence/Medical Records/EV-MR-001|EV-MR-001]]
- [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]
- [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

---

## Related Concepts
- [[Clinical/Diagnoses|Diagnoses]]
- [[Clinical/Medications|Medications]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Clinical/Diagnoses.md", """# Diagnoses: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## Current State
Active clinician-confirmed chronic diagnoses:
1. **Type 2 Diabetes Mellitus (ICD-10: E11)** — Chronic, stable
2. **Essential Hypertension (ICD-10: I10)** — Controlled
3. **Hyperlipidemia (ICD-10: E78.5)** — Controlled
4. **Bilateral Knee Osteoarthritis (ICD-10: M17.0)** — Chronic, symptomatic on exertion

---

## Baseline
All four diagnoses form the long-standing diagnostic baseline established prior to 2025.

---

## Clinical Information (Doctor)
- Diagnosed and monitored by Dr. S. Chandran, MD across routine outpatient reviews.
- Regular monitoring includes bimonthly vital sign checks and quarterly glycemic/renal blood panels.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]], [[Raw Evidence/Doctor/EV-DR-004|EV-DR-004]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## Caregiver Observations
Caregiver observations note physical symptoms corresponding to osteoarthritis (knee pain on walking) and assist with diabetes medication timing. Caregivers do not provide medical diagnoses.
*Evidence Reference: [[Raw Evidence/Caregiver/EV-CG-007|EV-CG-007]], [[Raw Evidence/Caregiver/EV-CG-015|EV-CG-015]], [[Raw Evidence/Caregiver/EV-CG-038|EV-CG-038]]*

---

## Historical Information
No history of neurological diagnoses (dementia, Parkinson's, stroke) or acute cardiac events documented in any record.
*Evidence Reference: [[Raw Evidence/Medical Records/EV-MR-001|EV-MR-001]]*

---

## AI-Derived Pattern
Diagnostic profile remains stable over the 9-month clinical surveillance window. No new clinical diagnosis has been added by physicians.

---

## Conflicts
- **Dementia Clarification**: Caregiver notes describe occasional confusion; however, there is **NO** clinician-confirmed diagnosis of dementia or cognitive impairment in the medical records.

---

## Unknown / Missing Information
- Last formal bone mineral density (DEXA) scan status.

---

## Evidence
- [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]
- [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]]
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]
- [[Raw Evidence/Medical Records/EV-MR-001|EV-MR-001]]

---

## Related Concepts
- [[Clinical/Medical History|Medical History]]
- [[Clinical/Medications|Medications]]
- [[Clinical/Laboratory History|Laboratory History]]
- [[Derived/Conflicts|Conflicts]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Clinical/Medications.md", """# Medications: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## Current State
The patient has four active pharmacological prescriptions. No additional medications exist in this dataset.

| Medication | Dose | Route | Frequency | Timing / Context | Indication | Status | Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Metformin** | 500 mg | Oral | Twice daily | Morning & Evening with meals | Type 2 Diabetes | ACTIVE | [[Raw Evidence/Medications/EV-MED-001|EV-MED-001]] |
| **Amlodipine** | 5 mg | Oral | Once daily | Morning | Hypertension | ACTIVE | [[Raw Evidence/Medications/EV-MED-002|EV-MED-002]] |
| **Atorvastatin** | 10 mg | Oral | Once nightly | Bedtime | Hyperlipidemia | ACTIVE | [[Raw Evidence/Medications/EV-MED-003|EV-MED-003]] |
| **Paracetamol** | 500 mg | Oral | PRN (as needed) | For knee discomfort (max 2g/day) | Osteoarthritis Pain | ACTIVE | [[Raw Evidence/Medications/EV-MED-004|EV-MED-004]] |

---

## Baseline
This 4-drug therapeutic regimen has remained unchanged since at least December 2025.

---

## Clinical Information (Doctor)
- Re-evaluated and confirmed unchanged by Dr. S. Chandran at each bimonthly review.
- Doctor notes family assists with weekly pill organization.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## Caregiver Observations
Caregiver logs document assisting with morning doses, organizing pillboxes, and providing occasional reminders for evening doses.
*Evidence Reference: [[Raw Evidence/Caregiver/EV-CG-009|EV-CG-009]], [[Raw Evidence/Caregiver/EV-CG-020|EV-CG-020]], [[Raw Evidence/Caregiver/EV-CG-033|EV-CG-033]], [[Raw Evidence/Caregiver/EV-CG-042|EV-CG-042]]*

---

## Historical Information
No documented adverse drug reactions, allergies, or pharmacological discontinuations.

---

## AI-Derived Pattern
Regimen adherence is high when supported by family pillbox prep. Potential clinical review item: Amlodipine 5mg timing relative to morning dizziness episodes on 2026-09-01.

---

## Conflicts
None.

---

## Unknown / Missing Information
- Exact adherence rate on days without explicit caregiver confirmation logs.

---

## Evidence
- [[Raw Evidence/Medications/EV-MED-001|EV-MED-001]]
- [[Raw Evidence/Medications/EV-MED-002|EV-MED-002]]
- [[Raw Evidence/Medications/EV-MED-003|EV-MED-003]]
- [[Raw Evidence/Medications/EV-MED-004|EV-MED-004]]
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

---

## Related Concepts
- [[Caregiver/Medication Adherence|Caregiver Medication Adherence]]
- [[Clinical/Diagnoses|Diagnoses]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Clinical/Doctor Assessments.md", """# Doctor Assessments: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## Current State
Serial clinical assessments conducted by Dr. S. Chandran, MD at Apollo Clinics, Chennai across 2025–2026.

---

## Chronological Assessment Log

### Assessment 1: 2025-12-15
- **Type**: Routine Consultation
- **Findings**: Stable T2DM, HTN, Hyperlipidemia, Bilateral Knee OA. Independent mobility, steady gait. Occasional benign forgetfulness noted. No acute neurological concerns.
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]

### Assessment 2: 2026-02-18
- **Type**: Bimonthly Follow-up
- **Findings**: Chronic conditions stable. HbA1c 7.1%. Intermittent knee discomfort. Ambulation independent. No falls reported since January slip.
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]]

### Assessment 3: 2026-04-12
- **Type**: Routine Follow-up
- **Findings**: BP 132/82 mmHg. Conditions stable. Independent mobility preserved. Benign forgetfulness without functional impairment.
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]]

### Assessment 4: 2026-06-14
- **Type**: Follow-up Examination
- **Findings**: Independent walking continues without aids. Occasional knee discomfort on prolonged standing. No falls reported.
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-004|EV-DR-004]]

### Assessment 5: 2026-08-18
- **Type**: Routine Review
- **Findings**: Patient ambulates independently into consultation room. No acute focal neurological deficits. Glycemic control stable (HbA1c 7.4%). Family assists with pill organization.
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

---

## Baseline
Consistently documents independent mobility, baseline orientation, and stable chronic disease status.

---

## AI-Derived Pattern
Clinical encounters capture periodic stable snapshots. The physician assessments document independent mobility and absence of acute symptoms up to 2026-08-18, just prior to the late-August / early-September caregiver observations.

---

## Conflicts
- Clinician documented independent mobility on 2026-08-18 ([[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]), whereas caregiver logs recorded progressive unsteadiness, support requirements, and a near-fall between 2026-08-24 and 2026-09-08 ([[Derived/Conflicts|Conflicts]]).

---

## Evidence
- [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]
- [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]]
- [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]]
- [[Raw Evidence/Doctor/EV-DR-004|EV-DR-004]]
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

---

## Related Concepts
- [[Clinical/Medical History|Medical History]]
- [[Clinical/Diagnoses|Diagnoses]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Clinical/Laboratory History.md", """# Laboratory History: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## Current State
Longitudinal laboratory biomarkers tracked quarterly from Metropolis Healthcare, Chennai.

| Assay | Reference Range | 2026-02-10 (EV-LAB-001) | 2026-05-12 (EV-LAB-002) | 2026-08-15 (EV-LAB-003) | Longitudinal Trajectory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HbA1c** | < 5.7% (Target < 7.5%) | **7.1%** | **7.3%** | **7.4%** | Mild upward drift within target |
| **Serum Creatinine** | 0.5 – 1.1 mg/dL | **0.9 mg/dL** | **0.9 mg/dL** | **0.9 mg/dL** | Completely stable renal function |
| **Serum Sodium** | 135 – 145 mmol/L | **138 mmol/L** | **139 mmol/L** | **137 mmol/L** | Euvolemic, normal range |
| **Serum Potassium** | 3.5 – 5.0 mmol/L | **4.3 mmol/L** | **4.2 mmol/L** | **4.3 mmol/L** | Stable electrolyte balance |
| **Hemoglobin** | 12.0 – 15.5 g/dL | **12.4 g/dL** | **12.2 g/dL** | **12.1 g/dL** | Stable, no anemia |

---

## Baseline
- Renal function baseline: Serum Creatinine 0.9 mg/dL.
- Electrolyte baseline: Sodium 137–139 mmol/L, Potassium 4.2–4.3 mmol/L.
- Hematology baseline: Hemoglobin 12.1–12.4 g/dL.

---

## Clinical Information (Doctor)
- Reviewed by Dr. Chandran; values interpreted as stable geriatric chronic disease control.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## Caregiver Observations
Caregivers are aware of blood test schedules and accompany patient for phlebotomy.

---

## AI-Derived Pattern
Renal function (Cr 0.9 mg/dL) and electrolytes remain stable across all three test dates, indicating that dizziness episodes in late August/September are unlikely to be driven by severe electrolyte dysregulation (hyponatremia/hypokalemia) or acute renal failure.

---

## Conflicts
None.

---

## Unknown / Missing Information
- Fasting blood glucose (spot) on days of dizziness episodes.

---

## Evidence
- [[Raw Evidence/Labs/EV-LAB-001|EV-LAB-001]]
- [[Raw Evidence/Labs/EV-LAB-002|EV-LAB-002]]
- [[Raw Evidence/Labs/EV-LAB-003|EV-LAB-003]]

---

## Related Concepts
- [[Clinical/Diagnoses|Diagnoses]]
- [[Caregiver/Dizziness|Dizziness]]
- [[Patient Overview]]
""")

# ==============================================================================
# 4. PATIENT WIKI - CAREGIVER SUBSPACE
# ==============================================================================

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Mobility.md", """# Caregiver Observation Log: Mobility

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001 (Daughter), CG002 (Son), CG003 (Family Caregiver)

---

## Current State
The caregiver log captures functional ambulation, postural stability, assistive support requirements, and walking speed inside and outside the home.

---

## Baseline
- Habitually ambulates independently inside and around the home.
- Does not routinely use a walking stick or frame.
*Evidence Reference: [[Raw Evidence/Patient/EV-PAT-002|EV-PAT-002]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]*

---

## Chronological Caregiver Observations

| Date | Observer | Verbatim Statement | Functional Interpretation | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-20** | CG001 | *"She is walking around the house normally."* | Normal independent mobility | [[Raw Evidence/Caregiver/EV-CG-001|EV-CG-001]] |
| **2026-08-24** | CG003 | *"She seemed slightly unsteady when getting up from the chair."* | Sit-to-stand unsteadiness | [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]] |
| **2026-08-27** | CG002 | *"She was holding the dining table for support while walking."* | Furniture cruising / support seeking | [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]] |
| **2026-08-30** | CG002 | *"She walked normally in the morning."* | Transient morning normalization | [[Raw Evidence/Caregiver/EV-CG-014|EV-CG-014]] |
| **2026-09-02** | CG002 | *"She needed someone's arm while walking outside."* | Physical human assistance for outdoors | [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]] |
| **2026-09-04** | CG003 | *"She was slower than usual while walking."* | Reduced gait velocity | [[Raw Evidence/Caregiver/EV-CG-025|EV-CG-025]] |
| **2026-09-06** | CG003 | *"She almost fell near the bathroom but I caught her."* | **NEAR_FALL** near bathroom | [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]] |
| **2026-09-08** | CG001 | *"She needed support to walk from the bedroom to the kitchen."* | Domestic indoor physical assistance | [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]] |
| **2026-09-09** | CG001 | *"She was walking better today and did not need support inside the house."* | **Improvement**: independent indoor walking | [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]] |

---

## Clinical Information (Doctor)
Physician recorded independent mobility on 2026-08-18 without assistive aids.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## AI-Derived Pattern
Caregiver records illustrate a progression: Independent → Unsteady → Furniture Support → Outdoor Arm Support → Slow Gait → Near-Fall → Indoor Support → Partial Indoor Recovery.
*Detailed Analysis: [[Derived/Mobility Trends|Mobility Trends]]*

---

## Conflicts
- Doctor documented independent ambulation on 2026-08-18; caregivers documented subsequent assistance needs and near-fall.
*Detailed Analysis: [[Derived/Conflicts|Conflicts]]*

---

## Unknown / Missing Information
- Quantitative gait speed or formal Timed Up and Go (TUG) measurements.

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-001|EV-CG-001]]
- [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]]
- [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]]
- [[Raw Evidence/Caregiver/EV-CG-014|EV-CG-014]]
- [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]]
- [[Raw Evidence/Caregiver/EV-CG-025|EV-CG-025]]
- [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]
- [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]]
- [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]]

---

## Related Concepts
- [[Caregiver/Falls|Falls]]
- [[Caregiver/Dizziness|Dizziness]]
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Falls.md", """# Caregiver Observation Log: Falls & Near-Falls

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG002, CG003

---

## Current State
Detailed documentation of historical fall events and recent balance incidents.

---

## Baseline
- One historical fall event approximately 8 months prior (January 2026).
- No documented fractures, intracranial injuries, or emergency hospitalizations.
*Evidence Reference: [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]], [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]*

---

## Explicit Event Categorization

### Historical Event (~8 Months Prior / January 2026)
- **Classification**: `FALL` (Completed ground-impact event)
- **Description**: Slipped on wet tile at home. Assisted up by family. Exam showed mild contusion, no fracture.
- **Evidence**: [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]], [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]], [[Raw Evidence/Doctor/EV-DR-002|EV-DR-002]]

### Recent Incident (2026-09-06)
- **Classification**: `NEAR_FALL` (**NOT A COMPLETED FALL**)
- **Description**: *"She almost fell near the bathroom but I caught her."* (Observer: CG003)
- **Impact / Injury**: None. Patient was intercepted before ground contact.
- **Evidence**: [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]

> [!IMPORTANT]
> **CRITICAL RULE**: EvoCare strictly distinguishes `FALL` from `NEAR_FALL`. A near-fall indicates loss of balance and balance impairment risk, but must **never** be mislabeled as a completed fall.

---

## AI-Derived Pattern
The patient experienced one completed fall 8 months ago and one near-fall on 2026-09-06 in the context of recent unsteadiness and dizziness.
*Detailed Analysis: [[Derived/Falls Trends|Falls Trends]]*

---

## Conflicts
- Doctor records document *"No recent falls reported"* at the 2026-08-18 visit. This is clinically accurate as the near-fall occurred subsequently on 2026-09-06, and was a near-fall rather than a completed fall.

---

## Unknown / Missing Information
- Lighting conditions and wetness of the bathroom floor on 2026-09-06 (`UNKNOWN`).

---

## Evidence
- [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]]
- [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]
- [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]

---

## Related Concepts
- [[Caregiver/Mobility|Mobility]]
- [[Caregiver/Dizziness|Dizziness]]
- [[Derived/Falls Trends|Falls Trends]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Dizziness.md", """# Caregiver Observation Log: Dizziness

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG003

---

## Current State
Recurring episodic dizziness reported by family caregivers between late August and early September 2026.

---

## Baseline
- No established persistent dizziness pattern documented in historical clinical records or baseline profile.
*Evidence Reference: [[Derived/Baseline|Baseline]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]*

---

## Chronological Dizziness Reports

| Date | Observer | Verbatim Statement | Documented Context | Severity / Duration / Cause | Evidence ID |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2026-08-23** | CG003 | *"He is dizzy."* | Ambiguous entry (pronoun slip) | Severity: `UNKNOWN`<br>Duration: `UNKNOWN`<br>Cause: `UNKNOWN` | [[Raw Evidence/Caregiver/EV-CG-043|EV-CG-043]] |
| **2026-08-25** | CG001 | *"She said she felt dizzy for a little while."* | Transient feeling | Severity: `UNKNOWN`<br>Duration: `UNKNOWN`<br>Cause: `UNKNOWN` | [[Raw Evidence/Caregiver/EV-CG-008|EV-CG-008]] |
| **2026-08-26** | CG001 | *"Follow-up regarding dizziness: severity not sure, duration unknown, no known fall occurred."* | Explicit follow-up inquiry | Severity: `Not sure`<br>Duration: `Unknown`<br>Fall: `No known fall` | [[Raw Evidence/Caregiver/EV-CG-010|EV-CG-010]] |
| **2026-09-01** | CG003 | *"She felt dizzy after getting out of bed but it went away after sitting down."* | **Postural / Orthostatic component**: Triggered by rising from bed, resolved on sitting | Severity: Mild-Moderate<br>Duration: Minutes<br>Cause: `UNKNOWN` (Postural trigger) | [[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]] |
| **2026-09-05** | CG001 | *"She complained of dizziness again in the evening."* | Evening recurrence | Severity: `UNKNOWN`<br>Duration: `UNKNOWN`<br>Cause: `UNKNOWN` | [[Raw Evidence/Caregiver/EV-CG-028|EV-CG-028]] |
| **2026-09-06** | CG003 | *"She felt dizzy and held the wall for a few seconds."* | Associated with balance instability, held wall | Duration: ~Few seconds<br>Cause: `UNKNOWN` | [[Raw Evidence/Caregiver/EV-CG-032|EV-CG-032]] |

---

## Clinical Information (Doctor)
No persistent dizziness complaints documented during clinic consultations up to 2026-08-18.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## AI-Derived Pattern
Repeated caregiver-reported dizziness has been observed across late August and early September. The underlying etiology has not been established. Postural changes noted on 2026-09-01 suggest orthostatic evaluation may be warranted.
*Detailed Analysis: [[Derived/Dizziness Trends|Dizziness Trends]]*

---

## Unknown / Missing Information
- Blood pressure during acute episodes (`UNKNOWN`).
- Heart rate or pulse rhythm during dizziness (`UNKNOWN`).
- Inner ear or vestibular signs (`UNKNOWN`).

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-008|EV-CG-008]]
- [[Raw Evidence/Caregiver/EV-CG-010|EV-CG-010]]
- [[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]]
- [[Raw Evidence/Caregiver/EV-CG-028|EV-CG-028]]
- [[Raw Evidence/Caregiver/EV-CG-032|EV-CG-032]]
- [[Raw Evidence/Caregiver/EV-CG-043|EV-CG-043]]

---

## Related Concepts
- [[Caregiver/Mobility|Mobility]]
- [[Caregiver/Falls|Falls]]
- [[Derived/Dizziness Trends|Dizziness Trends]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Cognition.md", """# Caregiver Observation Log: Cognition

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG002

---

## Current State
Longitudinal behavioral and cognitive notes recorded by family members.

---

## Baseline
- Occasional benign forgetfulness (misplacing glasses, keys).
- Fully recognizes family members and maintains active social conversation.
- **NO CLINICIAN-CONFIRMED DEMENTIA DIAGNOSIS**.
*Evidence Reference: [[Raw Evidence/Patient/EV-PAT-004|EV-PAT-004]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]]*

---

## Chronological Cognitive Observations

| Date | Observer | Verbatim Statement | Behavioral Context | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-21** | CG001 | *"She forgot where she kept her glasses."* | Baseline benign misplacement | [[Raw Evidence/Caregiver/EV-CG-002|EV-CG-002]] |
| **2026-08-28** | CG002 | *"She is confused."* | Ambiguous entry (`UNKNOWN` context) | [[Raw Evidence/Caregiver/EV-CG-045|EV-CG-045]] |
| **2026-08-29** | CG001 | *"She asked the same question twice in the evening."* | Repetitive questioning (evening) | [[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]] |
| **2026-09-02** | CG002 | *"She seemed confused about what day it was."* | Temporal disorientation note | [[Raw Evidence/Caregiver/EV-CG-022|EV-CG-022]] |
| **2026-09-04** | CG001 | *"She was completely normal and chatting with us in the morning."* | **Intact morning cognition & social chat** | [[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]] |
| **2026-09-07** | CG002 | *"She became confused again around dinner time."* | Evening confusion note | [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]] |
| **2026-09-09** | CG001 | *"She recognized everyone and was talking normally."* | **Full recognition & normal communication** | [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]] |

---

## Clinical Information (Doctor)
Doctor assessments repeatedly confirm benign forgetfulness without functional impairment or dementia diagnosis.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## AI-Derived Pattern
Intermittent caregiver-reported confusion has been observed, particularly during some evening periods. This pattern exhibits daily fluctuations and preserved morning clarity, with full family recognition documented on 2026-09-09. **This does not constitute dementia.**
*Detailed Analysis: [[Derived/Cognition Trends|Cognition Trends]]*

---

## Conflicts
- Caregivers note evening confusion, whereas clinic encounters during daytime hours document intact orientation.
*Detailed Analysis: [[Derived/Conflicts|Conflicts]]*

---

## Unknown / Missing Information
- Standardized cognitive screening scores (MMSE, MoCA).

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-002|EV-CG-002]]
- [[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]]
- [[Raw Evidence/Caregiver/EV-CG-022|EV-CG-022]]
- [[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]]
- [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]]
- [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]]
- [[Raw Evidence/Caregiver/EV-CG-045|EV-CG-045]]

---

## Related Concepts
- [[Caregiver/Behavior|Behavior]]
- [[Derived/Cognition Trends|Cognition Trends]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Nutrition.md", """# Caregiver Observation Log: Nutrition

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG002, CG003

---

## Current State
Meal intake, appetite variation, and hydration logs recorded by caregivers.

---

## Baseline
- Generally good appetite.
- Habitually completes full home-cooked meals.
*Evidence Reference: [[Raw Evidence/Patient/EV-PAT-003|EV-PAT-003]], [[Derived/Baseline|Baseline]]*

---

## Chronological Nutrition Observations

| Date | Observer | Verbatim Statement | Dietary Interpretation | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-22** | CG002 | *"She finished most of her lunch."* | Good intake (~80-90%) | [[Raw Evidence/Caregiver/EV-CG-003|EV-CG-003]] |
| **2026-08-28** | CG003 | *"She left about half of her lunch."* | Reduced intake (~50%) | [[Raw Evidence/Caregiver/EV-CG-012|EV-CG-012]] |
| **2026-08-31** | CG003 | *"She didn't eat much."* | Ambiguous (`UNKNOWN` quantity) | [[Raw Evidence/Caregiver/EV-CG-046|EV-CG-046]] |
| **2026-09-01** | CG001 | *"She ate less than usual at dinner."* | Reduced dinner portion | [[Raw Evidence/Caregiver/EV-CG-019|EV-CG-019]] |
| **2026-09-03** | CG001 | *"She only had a few bites of dinner."* | Significant dip (few bites) | [[Raw Evidence/Caregiver/EV-CG-023|EV-CG-023]] |
| **2026-09-05** | CG001 | *"Her appetite seemed better today."* | **Appetite recovery** | [[Raw Evidence/Caregiver/EV-CG-029|EV-CG-029]] |
| **2026-09-08** | CG001 | *"She ate about three quarters of her meal."* | **Sustained intake (~75%)** | [[Raw Evidence/Caregiver/EV-CG-037|EV-CG-037]] |

---

## Clinical Information (Doctor)
No chronic nutritional deficit documented in clinical reviews.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## AI-Derived Pattern
Recent caregiver observations show a period of reduced dietary intake between 2026-08-28 and 2026-09-03, followed by clear appetite improvement on 2026-09-05 and 2026-09-08. **This does not represent a diagnosis of malnutrition.**
*Detailed Analysis: [[Derived/Nutrition Trends|Nutrition Trends]]*

---

## Conflicts
None. Represents temporal daily fluctuation.

---

## Unknown / Missing Information
- Caloric or macronutrient breakdown (`UNKNOWN`).
- Daily fluid intake volume in milliliters (`UNKNOWN`).

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-003|EV-CG-003]]
- [[Raw Evidence/Caregiver/EV-CG-012|EV-CG-012]]
- [[Raw Evidence/Caregiver/EV-CG-019|EV-CG-019]]
- [[Raw Evidence/Caregiver/EV-CG-023|EV-CG-023]]
- [[Raw Evidence/Caregiver/EV-CG-029|EV-CG-029]]
- [[Raw Evidence/Caregiver/EV-CG-037|EV-CG-037]]
- [[Raw Evidence/Caregiver/EV-CG-046|EV-CG-046]]

---

## Related Concepts
- [[Derived/Nutrition Trends|Nutrition Trends]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Sleep.md", """# Caregiver Observation Log: Sleep

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observer: CG001 (Daughter)

---

## Current State
Nocturnal sleep duration and sleep quality observations recorded by family.

---

## Baseline
- Approximately 7 hours of nocturnal sleep.
- Occasional single nighttime waking to use bathroom.
*Evidence Reference: [[Derived/Baseline|Baseline]]*

---

## Chronological Sleep Observations

| Date | Observer | Verbatim Statement | Pattern Interpretation | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-23** | CG001 | *"Slept around 7 hours."* | Baseline normal duration | [[Raw Evidence/Caregiver/EV-CG-005|EV-CG-005]] |
| **2026-08-31** | CG001 | *"She woke up three times last night."* | Fragmented nocturnal sleep | [[Raw Evidence/Caregiver/EV-CG-017|EV-CG-017]] |
| **2026-09-03** | CG001 | *"She slept poorly."* | Restless / poor sleep quality | [[Raw Evidence/Caregiver/EV-CG-024|EV-CG-024]] |
| **2026-09-07** | CG001 | *"She slept better."* | **Improved nocturnal sleep** | [[Raw Evidence/Caregiver/EV-CG-035|EV-CG-035]] |

---

## Clinical Information (Doctor)
No formal sleep disorder (insomnia, sleep apnea) diagnosed in medical charts.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]*

---

## AI-Derived Pattern
Observations demonstrate transient sleep fragmentation around late August / early September with subsequent recovery on 2026-09-07. Represents normal physiological fluctuation rather than an established sleep disorder.
*Detailed Analysis: [[Derived/Sleep Trends|Sleep Trends]]*

---

## Unknown / Missing Information
- Polysomnography or wearable sleep tracking metrics (`UNKNOWN`).

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-005|EV-CG-005]]
- [[Raw Evidence/Caregiver/EV-CG-017|EV-CG-017]]
- [[Raw Evidence/Caregiver/EV-CG-024|EV-CG-024]]
- [[Raw Evidence/Caregiver/EV-CG-035|EV-CG-035]]

---

## Related Concepts
- [[Derived/Sleep Trends|Sleep Trends]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Pain.md", """# Caregiver Observation Log: Pain

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG002, CG003

---

## Current State
Exertional joint discomfort reports related to bilateral knee osteoarthritis.

---

## Baseline
- Occasional mild bilateral knee discomfort after prolonged walking or standing.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Derived/Baseline|Baseline]]*

---

## Chronological Pain Observations

| Date | Observer | Verbatim Statement | Pain Context | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-24** | CG003 | *"Her knees hurt a little after walking."* | Mild post-exertional knee pain | [[Raw Evidence/Caregiver/EV-CG-007|EV-CG-007]] |
| **2026-08-30** | CG002 | *"She said her knee pain was mild."* | Mild self-reported pain | [[Raw Evidence/Caregiver/EV-CG-015|EV-CG-015]] |
| **2026-09-04** | CG003 | *"She did not complain about knee pain today."* | **Pain-free day** | [[Raw Evidence/Caregiver/EV-CG-027|EV-CG-027]] |
| **2026-09-08** | CG002 | *"She said her knees hurt after going outside."* | Post-exertional knee pain outdoors | [[Raw Evidence/Caregiver/EV-CG-038|EV-CG-038]] |

---

## Clinical Information (Doctor)
Bilateral knee osteoarthritis diagnosed by Dr. Chandran; PRN Paracetamol 500mg prescribed.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Medications/EV-MED-004|EV-MED-004]]*

---

## AI-Derived Pattern
Knee discomfort fluctuates consistently with physical exertion and remains mild to moderate, aligning with known osteoarthritis. No acute joint swelling or red flag pain signs reported.

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-007|EV-CG-007]]
- [[Raw Evidence/Caregiver/EV-CG-015|EV-CG-015]]
- [[Raw Evidence/Caregiver/EV-CG-027|EV-CG-027]]
- [[Raw Evidence/Caregiver/EV-CG-038|EV-CG-038]]
- [[Raw Evidence/Medications/EV-MED-004|EV-MED-004]]

---

## Related Concepts
- [[Caregiver/Mobility|Mobility]]
- [[Clinical/Diagnoses|Diagnoses]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Behavior.md", """# Caregiver Observation Log: Behavior & Mood

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG002

---

## Current State
Daily mood, social interaction, and emotional demeanor recorded by family members.

---

## Baseline
- Calm, cheerful, socially engaged with family members and grandchildren.
*Evidence Reference: [[Derived/Baseline|Baseline]]*

---

## Chronological Behavior Observations

| Date | Observer | Verbatim Statement | Mood / Behavioral Context | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-22** | CG002 | *"She was in a good mood and talked with the family."* | Cheerful, socially engaged | [[Raw Evidence/Caregiver/EV-CG-004|EV-CG-004]] |
| **2026-08-30** | CG001 | *"She was quiet in the afternoon."* | Quiet demeanor (afternoon) | [[Raw Evidence/Caregiver/EV-CG-016|EV-CG-016]] |
| **2026-09-05** | CG002 | *"She was laughing and watching television with everyone."* | Cheerful, shared family entertainment | [[Raw Evidence/Caregiver/EV-CG-030|EV-CG-030]] |
| **2026-09-08** | CG001 | *"She seemed frustrated because she was walking slowly."* | Situational frustration linked to gait | [[Raw Evidence/Caregiver/EV-CG-039|EV-CG-039]] |

---

## Clinical Information (Doctor)
No psychiatric disorder (depression, anxiety, psychosis) documented in clinical files.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]*

---

## AI-Derived Pattern
Mood is generally positive and socially interactive. Occasional frustration on 2026-09-08 is situationally related to walking difficulties. **No psychiatric diagnosis inferred.**

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-004|EV-CG-004]]
- [[Raw Evidence/Caregiver/EV-CG-016|EV-CG-016]]
- [[Raw Evidence/Caregiver/EV-CG-030|EV-CG-030]]
- [[Raw Evidence/Caregiver/EV-CG-039|EV-CG-039]]

---

## Related Concepts
- [[Caregiver/Cognition|Cognition]]
- [[Caregiver/Mobility|Mobility]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Caregiver/Medication Adherence.md", """# Caregiver Observation Log: Medication Adherence

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Source Type: CAREGIVER | Observers: CG001, CG002

---

## Current State
Caregiver support with administration, weekly pillbox prep, and timing reminders.

---

## Baseline
- Family assists with pill organization and oversight.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Derived/Baseline|Baseline]]*

---

## Chronological Adherence Observations

| Date | Observer | Verbatim Statement | Adherence Context | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-26** | CG001 | *"She took her morning medicines with my help."* | Morning dose assisted | [[Raw Evidence/Caregiver/EV-CG-009|EV-CG-009]] |
| **2026-09-01** | CG001 | *"She almost forgot her evening medicine, so I reminded her."* | Evening reminder provided | [[Raw Evidence/Caregiver/EV-CG-020|EV-CG-020]] |
| **2026-09-06** | CG001 | *"I organized her medicines for the week."* | Weekly pill organizer sorted | [[Raw Evidence/Caregiver/EV-CG-033|EV-CG-033]] |
| **2026-09-09** | CG002 | *"She took her medicines on time today."* | On-time compliance | [[Raw Evidence/Caregiver/EV-CG-042|EV-CG-042]] |

---

## Clinical Information (Doctor)
Doctor records note family involvement in medication management.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]*

---

## AI-Derived Pattern
Caregivers report occasional need for medication reminders and active involvement in weekly pillbox organization. All logged doses were ultimately taken. **This does not represent a formal diagnosis of medication non-adherence.**

---

## Evidence
- [[Raw Evidence/Caregiver/EV-CG-009|EV-CG-009]]
- [[Raw Evidence/Caregiver/EV-CG-020|EV-CG-020]]
- [[Raw Evidence/Caregiver/EV-CG-033|EV-CG-033]]
- [[Raw Evidence/Caregiver/EV-CG-042|EV-CG-042]]
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

---

## Related Concepts
- [[Clinical/Medications|Medications]]
- [[Derived/Baseline|Baseline]]
- [[Patient Overview]]
""")

# ==============================================================================
# 5. PATIENT WIKI - DERIVED SUBSPACE
# ==============================================================================

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Baseline.md", """# Patient Functional Baseline: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Baseline Principles
The Patient Baseline represents the established, habitual physiological, cognitive, and functional status of the patient.
- **IMMUTABILITY**: This baseline is permanently preserved in the Knowledge Base.
- **NO OVERWRITING**: Acute fluctuations, temporary illnesses, or progressive functional declines never delete or overwrite this baseline.
- **REFERENCE ANCHOR**: All AI-derived trend and deviation metrics are calculated relative to this baseline.

---

## 2. Established Domain Baselines

### 2.1 Mobility
- **Baseline Status**: **Independently Mobile**
- **Description**: Ambulates independently around the home and local community without routine use of walking aids (canes, walkers).
- **Supporting Evidence**: [[Raw Evidence/Patient/EV-PAT-002|EV-PAT-002]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

### 2.2 Nutrition & Appetite
- **Baseline Status**: **Generally Good Appetite**
- **Description**: Enjoys home-cooked meals, consistently finishes full meal portions.
- **Supporting Evidence**: [[Raw Evidence/Patient/EV-PAT-003|EV-PAT-003]], [[Raw Evidence/Caregiver/EV-CG-003|EV-CG-003]]

### 2.3 Sleep
- **Baseline Status**: **~7 Hours Nocturnal Sleep**
- **Description**: Approximately 7 hours of sleep per night with occasional single nighttime waking.
- **Supporting Evidence**: [[Raw Evidence/Caregiver/EV-CG-005|EV-CG-005]]

### 2.4 Cognition & Memory
- **Baseline Status**: **Intact with Benign Forgetfulness**
- **Description**: Occasional benign forgetfulness (misplacing glasses/keys). Fully oriented to family, person, and surroundings. **No clinician-confirmed dementia diagnosis.**
- **Supporting Evidence**: [[Raw Evidence/Patient/EV-PAT-004|EV-PAT-004]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-003|EV-DR-003]]

### 2.5 Mood & Behavior
- **Baseline Status**: **Calm & Social**
- **Description**: Generally cheerful, emotionally stable, socially active with family and grandchildren.
- **Supporting Evidence**: [[Raw Evidence/Caregiver/EV-CG-004|EV-CG-004]], [[Raw Evidence/Caregiver/EV-CG-030|EV-CG-030]]

### 2.6 Pain
- **Baseline Status**: **Intermittent Mild Knee Discomfort**
- **Description**: Exertional knee discomfort related to bilateral Grade II osteoarthritis, managed with PRN paracetamol.
- **Supporting Evidence**: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Caregiver/EV-CG-015|EV-CG-015]]

### 2.7 Dizziness
- **Baseline Status**: **No Established Persistent Dizziness Pattern**
- **Description**: No recurrent vertiginous or presyncopal syndromes historically documented.
- **Supporting Evidence**: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

### 2.8 Falls History
- **Baseline Status**: **One Historical Fall (~8 Months Prior)**
- **Description**: One isolated slip in January 2026 without fracture or acute hospitalization.
- **Supporting Evidence**: [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]], [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]

### 2.9 Medication Management
- **Baseline Status**: **Family-Assisted Organization**
- **Description**: Patient takes medications reliably with family pillbox preparation and occasional reminders.
- **Supporting Evidence**: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Caregiver/EV-CG-033|EV-CG-033]]

---

## 3. Related References
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Cognition Trends|Cognition Trends]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Mobility Trends.md", """# Longitudinal Mobility Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Chronological Trajectory (Aug 20 – Sep 09, 2026)

```
2026-08-20: Independent indoor walking (EV-CG-001)
     ↓
2026-08-24: Slightly unsteady on sit-to-stand (EV-CG-006)
     ↓
2026-08-27: Holding dining table for support while walking (EV-CG-011)
     ↓
2026-08-30: Morning walking normal (EV-CG-014)
     ↓
2026-09-02: Needed someone's arm while walking outside (EV-CG-021)
     ↓
2026-09-04: Slower than usual walking pace (EV-CG-025)
     ↓
2026-09-06: NEAR_FALL near bathroom, caught by caregiver (EV-CG-031)
     ↓
2026-09-08: Needed support to walk from bedroom to kitchen (EV-CG-036)
     ↓
2026-09-09: PARTIAL IMPROVEMENT: Walking better today; did not need support inside house (EV-CG-040)
```

---

## 2. Multi-Source Evidence Table

| Date | Source Type | Source ID | Evidence ID | Observation / Finding | Functional Trajectory Stage |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2026-08-18** | DOCTOR | DR_CHANDRAN | [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]] | Ambulates independently into clinic | Baseline Independent |
| **2026-08-20** | CAREGIVER | CG001 | [[Raw Evidence/Caregiver/EV-CG-001|EV-CG-001]] | Walking around house normally | Baseline Independent |
| **2026-08-24** | CAREGIVER | CG003 | [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]] | Unsteady when getting up from chair | Initial Unsteadiness |
| **2026-08-27** | CAREGIVER | CG002 | [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]] | Holding dining table for support | Environmental Support |
| **2026-08-30** | CAREGIVER | CG002 | [[Raw Evidence/Caregiver/EV-CG-014|EV-CG-014]] | Walked normally in morning | Transient Normalization |
| **2026-09-02** | CAREGIVER | CG002 | [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]] | Needed arm support outside | Physical Support (Outdoor) |
| **2026-09-04** | CAREGIVER | CG003 | [[Raw Evidence/Caregiver/EV-CG-025|EV-CG-025]] | Slower walking pace | Bradykinesia / Caution |
| **2026-09-06** | CAREGIVER | CG003 | [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]] | Almost fell near bathroom (caught) | **NEAR_FALL** |
| **2026-09-08** | CAREGIVER | CG001 | [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]] | Support needed bedroom to kitchen | Physical Support (Indoor) |
| **2026-09-09** | CAREGIVER | CG001 | [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]] | Walking better, no support inside house | **Partial Domestic Recovery** |

---

## 3. AI-Derived Longitudinal Interpretation

> Recent caregiver observations suggest a **possible deviation from the previously documented independent mobility baseline**, characterized by progressive unsteadiness, furniture cruising, outdoor assistance needs, and a near-fall on 2026-09-06, followed by **partial improvement with independent indoor ambulation observed on 2026-09-09**.

- **Non-Diagnostic Stance**: This trend is an observational pattern and **NOT** a clinical diagnosis of permanent disability or gait ataxia.
- **Improvement Visibility**: The positive recovery recorded on 2026-09-09 (`EV-CG-040`) is explicitly retained in the trajectory.

---

## 4. Supporting Evidence
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]
- [[Raw Evidence/Caregiver/EV-CG-001|EV-CG-001]]
- [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]]
- [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]]
- [[Raw Evidence/Caregiver/EV-CG-014|EV-CG-014]]
- [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]]
- [[Raw Evidence/Caregiver/EV-CG-025|EV-CG-025]]
- [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]
- [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]]
- [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]]

---

## 5. Related Concepts
- [[Derived/Baseline|Baseline]]
- [[Derived/Falls Trends|Falls Trends]]
- [[Derived/Dizziness Trends|Dizziness Trends]]
- [[Derived/Conflicts|Conflicts]]
- [[Caregiver/Mobility|Caregiver Mobility Log]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Cognition Trends.md", """# Longitudinal Cognition Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Chronological Cognitive Log

| Date | Source | Evidence ID | Observation | Cognitive Domain | Functional Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **2026-08-18** | DOCTOR | [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]] | No acute neurological deficits | Clinical Exam | Normal Baseline |
| **2026-08-21** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-002|EV-CG-002]] | Forgot where she kept her glasses | Memory (Objects) | Benign Forgetfulness |
| **2026-08-29** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]] | Asked same question twice in evening | Short-term Memory | Evening Repetition |
| **2026-09-02** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-022|EV-CG-022]] | Confused about what day it was | Orientation (Time) | Transient Disorientation |
| **2026-09-04** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]] | Completely normal & chatting in morning | Communication / Social | **Intact Cognition** |
| **2026-09-07** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]] | Confused again around dinner time | Orientation / Awareness | Evening Disorientation |
| **2026-09-09** | CAREGIVER | [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]] | Recognized everyone & talking normally | Person Recognition | **Intact Cognition** |

---

## 2. AI-Derived Longitudinal Interpretation

> Intermittent caregiver-reported confusion has been observed, particularly during some evening periods (2026-08-29, 2026-09-02, 2026-09-07). This alternates with fully clear morning communication (2026-09-04) and intact recognition of all family members (2026-09-09).

> [!IMPORTANT]
> **NO DEMENTIA DIAGNOSIS**: There is **NO** clinician-confirmed dementia diagnosis in this dataset. Caregiver observations of intermittent confusion are non-diagnostic and may correlate with fatigue, sleep fragmentation, or metabolic variation.

---

## 3. Supporting Evidence
- [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]
- [[Raw Evidence/Caregiver/EV-CG-002|EV-CG-002]]
- [[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]]
- [[Raw Evidence/Caregiver/EV-CG-022|EV-CG-022]]
- [[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]]
- [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]]
- [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]]

---

## 4. Related Concepts
- [[Derived/Baseline|Baseline]]
- [[Caregiver/Cognition|Caregiver Cognition Log]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Nutrition Trends.md", """# Longitudinal Nutrition Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Chronological Intake Trajectory

```
2026-08-22: Finished most of lunch (~80-90%) (EV-CG-003)
     ↓
2026-08-28: Left about half of lunch (~50%) (EV-CG-012)
     ↓
2026-09-01: Ate less than usual at dinner (EV-CG-019)
     ↓
2026-09-03: Significant reduction: only a few bites of dinner (EV-CG-023)
     ↓
2026-09-05: APPETITE IMPROVEMENT: Appetite seemed better today (EV-CG-029)
     ↓
2026-09-08: SUSTAINED RECOVERY: Ate about three quarters of meal (~75%) (EV-CG-037)
```

---

## 2. AI-Derived Longitudinal Interpretation

> Recent caregiver observations show a **period of reduced dietary intake between 2026-08-28 and 2026-09-03**, followed by **clear appetite improvement and sustained meal completion on 2026-09-05 and 2026-09-08**.

- **Non-Diagnostic Stance**: This is an observational dietary fluctuation and **NOT** a diagnosis of clinical malnutrition or anorexia.

---

## 3. Supporting Evidence
- [[Raw Evidence/Caregiver/EV-CG-003|EV-CG-003]]
- [[Raw Evidence/Caregiver/EV-CG-012|EV-CG-012]]
- [[Raw Evidence/Caregiver/EV-CG-019|EV-CG-019]]
- [[Raw Evidence/Caregiver/EV-CG-023|EV-CG-023]]
- [[Raw Evidence/Caregiver/EV-CG-029|EV-CG-029]]
- [[Raw Evidence/Caregiver/EV-CG-037|EV-CG-037]]

---

## 4. Related Concepts
- [[Derived/Baseline|Baseline]]
- [[Caregiver/Nutrition|Caregiver Nutrition Log]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Sleep Trends.md", """# Longitudinal Sleep Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Chronological Sleep Log

| Date | Evidence ID | Observation | Nocturnal Trajectory |
| :--- | :--- | :--- | :--- |
| **2026-08-23** | [[Raw Evidence/Caregiver/EV-CG-005|EV-CG-005]] | Slept around 7 hours | Normal Baseline Duration |
| **2026-08-31** | [[Raw Evidence/Caregiver/EV-CG-017|EV-CG-017]] | Woke up three times last night | Sleep Fragmentation |
| **2026-09-03** | [[Raw Evidence/Caregiver/EV-CG-024|EV-CG-024]] | Slept poorly | Poor Quality / Restlessness |
| **2026-09-07** | [[Raw Evidence/Caregiver/EV-CG-035|EV-CG-035]] | Slept better | **Recovery to Restful Sleep** |

---

## 2. AI-Derived Longitudinal Interpretation

> Caregiver reports reflect transient nocturnal sleep fragmentation and restlessness between late August and early September, followed by documented sleep recovery on 2026-09-07. This represents physiological sleep variability rather than a clinical sleep disorder.

---

## 3. Supporting Evidence
- [[Raw Evidence/Caregiver/EV-CG-005|EV-CG-005]]
- [[Raw Evidence/Caregiver/EV-CG-017|EV-CG-017]]
- [[Raw Evidence/Caregiver/EV-CG-024|EV-CG-024]]
- [[Raw Evidence/Caregiver/EV-CG-035|EV-CG-035]]

---

## 4. Related Concepts
- [[Derived/Baseline|Baseline]]
- [[Caregiver/Sleep|Caregiver Sleep Log]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Dizziness Trends.md", """# Longitudinal Dizziness Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Chronological Dizziness Trajectory

```
2026-08-25: Felt dizzy for a little while (EV-CG-008) [Severity/Duration UNKNOWN]
     ↓
2026-08-26: Follow-up check: severity not sure, duration unknown, no fall (EV-CG-010)
     ↓
2026-09-01: Felt dizzy after getting out of bed, resolved after sitting down (EV-CG-018) [Postural Trigger]
     ↓
2026-09-05: Complained of dizziness again in evening (EV-CG-028)
     ↓
2026-09-06: Felt dizzy and held wall for a few seconds (EV-CG-032) [Balance Instability]
```

---

## 2. AI-Derived Longitudinal Interpretation

> Repeated caregiver-reported dizziness has been observed across late August and early September 2026. The underlying etiology has **not** been established. Postural characteristics noted on 2026-09-01 (triggered on getting out of bed, relieved by sitting) suggest orthostatic hypotension or vestibular disturbance should be evaluated clinically by an MD.

> [!WARNING]
> **NO ETIOLOGICAL DIAGNOSIS**: EvoCare strictly avoids diagnosing the medical cause (e.g., vertigo, orthostatic hypotension, cardiac arrhythmia, medication effect). This determination is reserved for the physician.

---

## 3. Supporting Evidence
- [[Raw Evidence/Caregiver/EV-CG-008|EV-CG-008]]
- [[Raw Evidence/Caregiver/EV-CG-010|EV-CG-010]]
- [[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]]
- [[Raw Evidence/Caregiver/EV-CG-028|EV-CG-028]]
- [[Raw Evidence/Caregiver/EV-CG-032|EV-CG-032]]

---

## 4. Related Concepts
- [[Caregiver/Dizziness|Caregiver Dizziness Log]]
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Falls Trends|Falls Trends]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Falls Trends.md", """# Longitudinal Falls & Balance Trends: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

---

## 1. Longitudinal Event Summary

```
+-------------------------------------------------------------------------------+
| DATE        | CLASSIFICATION | DESCRIPTION                     | OUTCOME      |
+-------------+----------------+---------------------------------+--------------+
| Jan 2026    | FALL           | Slipped on wet tile at home;    | Contusion;   |
| (~8 mo ago) | (Historical)   | assisted up by family           | NO fracture  |
|             |                | Evidence: EV-PAT-001, EV-MR-002 |              |
+-------------+----------------+---------------------------------+--------------+
| 2026-09-06  | NEAR_FALL      | Almost fell near bathroom;      | NO fall;     |
| (Recent)    | (Balance Loss) | caught by caregiver CG003       | NO injury    |
|             |                | Evidence: EV-CG-031             |              |
+-------------------------------------------------------------------------------+
```

---

## 2. AI-Derived Longitudinal Interpretation

> The longitudinal record documents **one historical completed fall approximately 8 months prior** (Jan 2026) without fracture, and **one recent near-fall on 2026-09-06** where the caregiver intercepted the patient before impact.

- **Distinction**: `NEAR_FALL` is distinct from a `FALL`. The patient did not experience a completed ground-impact fall in September 2026.
- **Risk Profile**: The near-fall occurred during a cluster of caregiver-reported dizziness and mobility changes, indicating increased fall risk for clinical attention.

---

## 3. Supporting Evidence
- [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]]
- [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]]
- [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]

---

## 4. Related Concepts
- [[Caregiver/Falls|Caregiver Falls Log]]
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts.md", """# Multi-Source Conflicts & Discrepancies: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

EvoCare preserves contradictions and temporal differences across sources rather than silently resolving them. This document analyzes detected differences requiring clinician adjudication.

---

## 1. Conflict Case #1: Mobility Independence vs. Assistance Needs

### Doctor View
- **Finding**: *"Patient ambulates independently into consultation room with steady pace... independent mobility."*
- **Source**: Doctor (Dr. S. Chandran)
- **Date**: 2026-08-18
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

### Caregiver View
- **Finding**: *"She seemed slightly unsteady... holding table... needed someone's arm... almost fell near bathroom... needed support bedroom to kitchen."*
- **Source**: Caregivers (CG001, CG002, CG003)
- **Dates**: 2026-08-24 to 2026-09-08
- **Evidence**: [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]], [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]], [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]], [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]], [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]]

### Status & Clinical Explanation
- **Status**: `CONFLICTING / REQUIRES CLINICIAN REVIEW`
- **Analysis**: The clinical visit on 2026-08-18 preceded the onset of caregiver-observed unsteadiness which started on 2026-08-24. The doctor evaluated the patient in a controlled clinic setting prior to the home-based decline. The Knowledge Base **does not declare a winner**; both records are preserved for the physician's next consultation.

---

## 2. Discrepancy Case #2: Fall History vs. Recent Near-Fall

### Doctor Documentation
- **Finding**: *"No recent falls reported."*
- **Source**: Doctor
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-004|EV-DR-004]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]]

### Caregiver Observation
- **Finding**: *"She almost fell near the bathroom but I caught her."*
- **Source**: Caregiver (CG003)
- **Date**: 2026-09-06
- **Evidence**: [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]

### Status & Clinical Explanation
- **Status**: `NON-CONTRADICTORY TEMPORAL / DEFINITIONAL DIFFERENCE`
- **Analysis**: This is not a contradiction because:
  1. The near-fall occurred on 2026-09-06, after the last clinical consultation on 2026-08-18.
  2. **`FALL` ≠ `NEAR_FALL`**: The caregiver caught the patient before floor contact. No completed fall occurred.

---

## 3. Discrepancy Case #3: Stable Appetite vs. Transient Reduced Intake

### Doctor Documentation
- **Finding**: Stable chronic nutritional and metabolic status; HbA1c 7.4%.
- **Source**: Doctor & Labs
- **Evidence**: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Labs/EV-LAB-003|EV-LAB-003]]

### Caregiver Observation
- **Finding**: Reduced intake and appetite dip between 2026-08-28 and 2026-09-03 (*"left half of lunch"*, *"few bites of dinner"*).
- **Source**: Caregivers (CG001, CG003)
- **Evidence**: [[Raw Evidence/Caregiver/EV-CG-012|EV-CG-012]], [[Raw Evidence/Caregiver/EV-CG-023|EV-CG-023]]

### Status & Clinical Explanation
- **Status**: `TEMPORAL FLUCTUATION`
- **Analysis**: Caregiver logs capture short-term daily dietary fluctuations that recovered on 2026-09-05 (`EV-CG-029`), which do not contradict overall chronic metabolic stability.

---

## 4. Unknown / Missing Information Requiring Adjudication
- Formal orthostatic blood pressure measurements (supine vs. standing).
- Comprehensive geriatric balance and gait assessment.

---

## 5. Related References
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Falls Trends|Falls Trends]]
- [[Derived/Patient Memory Summary|Patient Memory Summary]]
- [[Patient Overview]]
""")

write_file("Patient Wiki/P001 Meenakshi Raman/Derived/Patient Memory Summary.md", """# Patient Memory Summary: Meenakshi Raman (P001)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**  
> Patient: Meenakshi Raman | ID: P001 | Age: 78 | Location: Chennai, TN

---

## 1. High-Level Executive Memory Brief

Historically, the patient has been documented as independently mobile without assistive devices ([[Raw Evidence/Patient/EV-PAT-002|EV-PAT-002]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]]). Recent caregiver observations from late August through early September 2026 describe intermittent unsteadiness, furniture support, and an increasing need for walking assistance ([[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]], [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]], [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]], [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]]), including a **near-fall near the bathroom on 2026-09-06** where the caregiver intercepted her before impact ([[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]). 

The latest caregiver observation on **2026-09-09 indicates improvement**, with the patient walking better inside the house without requiring support ([[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]]). 

Alongside mobility changes, caregivers reported recurrent episodic dizziness—notably with a postural component upon getting out of bed on 2026-09-01 ([[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]])—and transient evening confusion notes ([[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]], [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]]) which alternated with intact morning cognition and full family recognition on 2026-09-09 ([[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]], [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]]).

The underlying etiology of the recent mobility and dizziness episodes has **not been established**. The patient has no clinician-confirmed dementia diagnosis. Chronic medical conditions (T2DM, Hypertension, Hyperlipidemia, Knee Osteoarthritis) and recent laboratory biomarkers (HbA1c 7.4%, Cr 0.9 mg/dL on 2026-08-15) remain stable.

---

## 2. Key Synthesis Domains

```
+-------------------------------------------------------------------------------+
| DOMAIN      | BASELINE           | RECENT OBSERVATIONS     | CURRENT STATUS   |
+-------------+--------------------+-------------------------+------------------+
| Mobility    | Independent        | Unsteady, support used, | Improved indoor  |
|             | (EV-PAT-002)       | near-fall (EV-CG-031)   | walking (EV-040) |
+-------------+--------------------+-------------------------+------------------+
| Dizziness   | No persistent      | Recurrent episodes,     | Episodic; cause  |
|             | pattern (EV-DR-001)| postural on 09-01       | UNKNOWN          |
+-------------+--------------------+-------------------------+------------------+
| Cognition   | Benign forgetful   | Evening confusion notes | Morning clarity; |
|             | NO dementia        | (EV-CG-013, 034)        | full recognition |
+-------------+--------------------+-------------------------+------------------+
| Nutrition   | Good appetite      | Reduced intake 08-28    | Recovered intake |
|             | (EV-PAT-003)       | to 09-03 (EV-CG-023)    | 09-08 (EV-CG-037)|
+-------------+--------------------+-------------------------+------------------+
| Falls       | 1 slip 8 mo ago    | 1 NEAR_FALL on 09-06    | NO recent        |
|             | (EV-MR-002)        | (EV-CG-031)             | completed fall   |
+-------------------------------------------------------------------------------+
```

---

## 3. Active Clinical Review Items for Attending Physician
1. **Mobility & Gait Evaluation**: Assess gait stability and determine if physical therapy or assistive devices are indicated given the recent decline and recovery.
2. **Orthostatic / Cardiovascular Evaluation**: Check postural vitals to investigate dizziness upon rising (2026-09-01) and evaluate Amlodipine timing.
3. **Cognitive Contextualization**: Note evening confusion pattern for formal clinical screening if symptoms persist.

---

## 4. Supporting Evidence Directory
- **Clinical & Lab Records**: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Labs/EV-LAB-003|EV-LAB-003]], [[Raw Evidence/Medications/EV-MED-001|EV-MED-001]]
- **Caregiver Trend Records**: [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]], [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]], [[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]], [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]], [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]], [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]], [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]]

---

## 5. Related References
- [[Derived/Baseline|Baseline]]
- [[Derived/Mobility Trends|Mobility Trends]]
- [[Derived/Conflicts|Conflicts]]
- [[Patient Overview]]
""")

# ==============================================================================
# 6. DEMO QUESTIONS & EXPECTED ANSWERS
# ==============================================================================

write_file("Demo/Demo Questions.md", """# EvoCare Demo Questions (Evaluation Suite)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

The following 15 evaluation questions demonstrate how EvoCare answers complex clinical and longitudinal inquiries strictly grounded in the Knowledge Base without hallucinations or unsupported diagnostic inferences.

---

## Question 1: Baseline Mobility
What is the patient's normal mobility baseline?

## Question 2: Recent Mobility Changes
What changed in her mobility recently?

## Question 3: Recent Caregiver Mobility Observations
Show the recent caregiver observations about mobility.

## Question 4: Fall History Confirmation
Did she have a recent fall?

## Question 5: Near-Fall Verification
Did she have a near fall?

## Question 6: Recurrent Dizziness
Has dizziness been recurring?

## Question 7: Nutritional Trajectory
What happened to her appetite?

## Question 8: Cognitive Status vs. Baseline
Has her cognition changed from baseline?

## Question 9: Multi-Source Conflicts
What conflicts exist between doctor records and caregiver observations?

## Question 10: Unknown Information
What information is unknown?

## Question 11: Recent Improvements
What recent observations indicate improvement?

## Question 12: Mobility Decline Evidence
What evidence supports the possible mobility decline?

## Question 13: Dementia Verification
Does the patient have dementia?

## Question 14: Permanent Disability Inquiry
Is the patient permanently unable to walk independently?

## Question 15: Clinical Investigation Plan
What information would a doctor need to investigate the recent mobility change?

---

## Related References
- [[Demo/Expected Answers|Expected Answers]]
- [[Patient Wiki/P001 Meenakshi Raman/Derived/Patient Memory Summary|Patient Memory Summary]]
- [[Patient Wiki/P001 Meenakshi Raman/Patient Overview|Patient Overview]]
""")

write_file("Demo/Expected Answers.md", """# EvoCare Expected Answers (Grounded Evaluation Suite)

> **FABRICATED / SYNTHETIC DEMO PATIENT DATASET REFERENCE**

The answers below are grounded strictly in the EvoCare Knowledge Base with exact Evidence ID citations.

---

### Question 1: What is the patient's normal mobility baseline?
**Grounded Answer:**
The patient's documented normal baseline is **independent mobility**. She habitually walks around the house and community without routine use of a walking stick or frame.  
*Evidence Citations: [[Raw Evidence/Patient/EV-PAT-002|EV-PAT-002]], [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Baseline|Derived Baseline]]*

---

### Question 2: What changed in her mobility recently?
**Grounded Answer:**
Between 2026-08-24 and 2026-09-08, caregivers observed progressive unsteadiness upon standing, furniture cruising, needing human arm support for outdoor walking, a slower pace, domestic support needs, and a near-fall on 2026-09-06. However, on 2026-09-09, she showed partial improvement and walked without support inside the house.  
*Evidence Citations: [[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]], [[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]], [[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]], [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]], [[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]], [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Mobility Trends|Mobility Trends]]*

---

### Question 3: Show the recent caregiver observations about mobility.
**Grounded Answer:**
- **2026-08-20**: *"She is walking around the house normally."* ([[Raw Evidence/Caregiver/EV-CG-001|EV-CG-001]])
- **2026-08-24**: *"She seemed slightly unsteady when getting up from the chair."* ([[Raw Evidence/Caregiver/EV-CG-006|EV-CG-006]])
- **2026-08-27**: *"She was holding the dining table for support while walking."* ([[Raw Evidence/Caregiver/EV-CG-011|EV-CG-011]])
- **2026-08-30**: *"She walked normally in the morning."* ([[Raw Evidence/Caregiver/EV-CG-014|EV-CG-014]])
- **2026-09-02**: *"She needed someone's arm while walking outside."* ([[Raw Evidence/Caregiver/EV-CG-021|EV-CG-021]])
- **2026-09-04**: *"She was slower than usual while walking."* ([[Raw Evidence/Caregiver/EV-CG-025|EV-CG-025]])
- **2026-09-06**: *"She almost fell near the bathroom but I caught her."* ([[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]])
- **2026-09-08**: *"She needed support to walk from the bedroom to the kitchen."* ([[Raw Evidence/Caregiver/EV-CG-036|EV-CG-036]])
- **2026-09-09**: *"She was walking better today and did not need support inside the house."* ([[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]])

---

### Question 4: Did she have a recent fall?
**Grounded Answer:**
**No.** There is no documented recent completed fall in the recent observation timeline (August–September 2026). The only completed fall occurred approximately 8 months prior in January 2026 with no fracture. The incident on 2026-09-06 was intercepted by a caregiver and is classified strictly as a `NEAR_FALL`.  
*Evidence Citations: [[Raw Evidence/Patient/EV-PAT-001|EV-PAT-001]], [[Raw Evidence/Medical Records/EV-MR-002|EV-MR-002]], [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Falls Trends|Falls Trends]]*

---

### Question 5: Did she have a near fall?
**Grounded Answer:**
**Yes.** On 2026-09-06, caregiver CG003 reported: *"She almost fell near the bathroom but I caught her."* This event is classified as `NEAR_FALL`.  
*Evidence Citation: [[Raw Evidence/Caregiver/EV-CG-031|EV-CG-031]]*

---

### Question 6: Has dizziness been recurring?
**Grounded Answer:**
**Yes.** Repeated episodic dizziness was reported on 2026-08-25, 2026-09-01 (postural: occurred upon getting out of bed and resolved upon sitting), 2026-09-05 (evening), and 2026-09-06 (held wall for a few seconds). The medical etiology has not been established.  
*Evidence Citations: [[Raw Evidence/Caregiver/EV-CG-008|EV-CG-008]], [[Raw Evidence/Caregiver/EV-CG-018|EV-CG-018]], [[Raw Evidence/Caregiver/EV-CG-028|EV-CG-028]], [[Raw Evidence/Caregiver/EV-CG-032|EV-CG-032]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Dizziness Trends|Dizziness Trends]]*

---

### Question 7: What happened to her appetite?
**Grounded Answer:**
Her appetite experienced a temporary reduction between 2026-08-28 and 2026-09-03 (leaving half of lunch on 08-28, eating less on 09-01, having only a few bites on 09-03). This was followed by documented appetite recovery on 2026-09-05 and completing ~75% of her meal on 2026-09-08.  
*Evidence Citations: [[Raw Evidence/Caregiver/EV-CG-012|EV-CG-012]], [[Raw Evidence/Caregiver/EV-CG-019|EV-CG-019]], [[Raw Evidence/Caregiver/EV-CG-023|EV-CG-023]], [[Raw Evidence/Caregiver/EV-CG-029|EV-CG-029]], [[Raw Evidence/Caregiver/EV-CG-037|EV-CG-037]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Nutrition Trends|Nutrition Trends]]*

---

### Question 8: Has her cognition changed from baseline?
**Grounded Answer:**
Caregivers reported intermittent evening confusion episodes on 2026-08-29, 2026-09-02, and 2026-09-07. However, this alternated with completely normal morning conversation on 2026-09-04 and full recognition of family members and normal talking on 2026-09-09. Baseline occasional forgetfulness is preserved, and there is no confirmed diagnosis of dementia.  
*Evidence Citations: [[Raw Evidence/Caregiver/EV-CG-013|EV-CG-013]], [[Raw Evidence/Caregiver/EV-CG-022|EV-CG-022]], [[Raw Evidence/Caregiver/EV-CG-026|EV-CG-026]], [[Raw Evidence/Caregiver/EV-CG-034|EV-CG-034]], [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Cognition Trends|Cognition Trends]]*

---

### Question 9: What conflicts exist between doctor records and caregiver observations?
**Grounded Answer:**
1. **Mobility Status**: Doctor documented independent mobility on 2026-08-18 (`EV-DR-005`), whereas caregivers documented unsteadiness, support needs, and a near-fall between 2026-08-24 and 2026-09-08 (`EV-CG-006` to `EV-CG-036`).
2. **Fall Reporting**: Doctor documented no recent falls (which was accurate as of the clinic visit, and subsequent 09-06 event was a near-fall).
3. **Cognitive Presentation**: Doctor observed alert, intact orientation during daytime clinic visits, while caregivers noted intermittent evening confusion.  
*Evidence Citation: [[Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts|Derived Conflicts]]*

---

### Question 10: What information is unknown?
**Grounded Answer:**
1. The exact duration, severity, and blood pressure/heart rate values during dizziness episodes.
2. The specific environmental triggers for the bathroom near-fall.
3. Standardized cognitive test scores (e.g., MMSE, MoCA).
4. Missing details from ambiguous caregiver logs (`EV-CG-043` to `EV-CG-047`).  
*Evidence Citation: [[Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts|Conflicts & Unknowns]]*

---

### Question 11: What recent observations indicate improvement?
**Grounded Answer:**
1. **Mobility (2026-09-09)**: *"She was walking better today and did not need support inside the house."* (`EV-CG-040`)
2. **Cognition (2026-09-09)**: *"She recognized everyone and was talking normally."* (`EV-CG-041`)
3. **Medication (2026-09-09)**: *"She took her medicines on time today."* (`EV-CG-042`)
4. **Nutrition (2026-09-08)**: *"She ate about three quarters of her meal."* (`EV-CG-037`)
5. **Sleep (2026-09-07)**: *"She slept better."* (`EV-CG-035`)

---

### Question 12: What evidence supports the possible mobility decline?
**Grounded Answer:**
The pattern is supported by 7 distinct caregiver evidence records:
- Unsteadiness on chair rise: `EV-CG-006`
- Furniture cruising: `EV-CG-011`
- Outdoor arm support: `EV-CG-021`
- Slow walking pace: `EV-CG-025`
- Near-fall near bathroom: `EV-CG-031`
- Domestic walking support: `EV-CG-036`
- Frustration with gait speed: `EV-CG-039`

---

### Question 13: Does the patient have dementia?
**Grounded Answer:**
**No such diagnosis exists in the records.** The dataset contains intermittent caregiver-reported evening confusion and benign forgetfulness, but there is **no clinician-confirmed dementia diagnosis** in any medical record. Intact daytime clarity and full family recognition remain documented as recently as 2026-09-09 (`EV-CG-041`).  
*Evidence Citations: [[Raw Evidence/Doctor/EV-DR-001|EV-DR-001]], [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Caregiver/EV-CG-041|EV-CG-041]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Cognition Trends|Cognition Trends]]*

---

### Question 14: Is the patient permanently unable to walk independently?
**Grounded Answer:**
**No such conclusion can be made.** Historical records document independent mobility, recent observations showed increased support needs, and the latest observation on 2026-09-09 explicitly documents partial recovery (*"walking better today and did not need support inside the house"*).  
*Evidence Citations: [[Raw Evidence/Doctor/EV-DR-005|EV-DR-005]], [[Raw Evidence/Caregiver/EV-CG-040|EV-CG-040]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Mobility Trends|Mobility Trends]]*

---

### Question 15: What information would a doctor need to investigate the recent mobility change?
**Grounded Answer:**
To evaluate the recent mobility deviation, an attending physician would require:
1. **Orthostatic Vital Signs**: Lying and standing blood pressure and heart rate to investigate postural dizziness.
2. **Medication Review**: Assessing Amlodipine 5mg timing and potential antihypertensive-induced presyncope.
3. **Physical & Neurological Exam**: Timed Up and Go (TUG) test, cerebellar testing, Romberg test, and knee osteoarthritis joint exam.
4. **Environmental Assessment**: Home bathroom lighting and grab-bar installation.
5. **Standardized Cognitive Screening**: MMSE or MoCA to contextualize evening confusion reports.  
*Evidence Citations: [[Patient Wiki/P001 Meenakshi Raman/Derived/Patient Memory Summary|Patient Memory Summary]], [[Patient Wiki/P001 Meenakshi Raman/Derived/Conflicts|Derived Conflicts]]*
""")

print("Successfully generated all files in EvoCare Knowledge Base!")
