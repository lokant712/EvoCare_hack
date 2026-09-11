# Multi-Source Conflicts & Discrepancies: Meenakshi Raman (P001)

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
