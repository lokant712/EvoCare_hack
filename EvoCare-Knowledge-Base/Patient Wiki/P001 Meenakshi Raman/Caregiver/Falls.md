# Caregiver Observation Log: Falls & Near-Falls

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
- [[Raw Evidence/Caregiver/EV-CG-482|EV-CG-482]]
- [[Raw Evidence/Caregiver/EV-CG-457|EV-CG-457]]
- [[Raw Evidence/Caregiver/EV-CG-432|EV-CG-432]]
- [[Raw Evidence/Caregiver/EV-CG-407|EV-CG-407]]
- [[Raw Evidence/Caregiver/EV-CG-382|EV-CG-382]]
- [[Raw Evidence/Caregiver/EV-CG-357|EV-CG-357]]
- [[Raw Evidence/Caregiver/EV-CG-332|EV-CG-332]]
- [[Raw Evidence/Caregiver/EV-CG-280|EV-CG-280]]
- [[Raw Evidence/Caregiver/EV-CG-255|EV-CG-255]]
- [[Raw Evidence/Caregiver/EV-CG-230|EV-CG-230]]
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
