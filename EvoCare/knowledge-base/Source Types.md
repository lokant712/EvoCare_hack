# EvoCare Source Types

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
