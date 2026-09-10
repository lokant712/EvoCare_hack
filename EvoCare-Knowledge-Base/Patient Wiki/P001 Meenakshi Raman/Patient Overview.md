# Patient Overview: Meenakshi Raman (P001)

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
