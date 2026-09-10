# EvoCare Knowledge Base — Longitudinal Patient Memory System

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
