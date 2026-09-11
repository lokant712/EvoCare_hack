# EvoCare Memory Rules & Invariants

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
