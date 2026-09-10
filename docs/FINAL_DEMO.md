# EvoCare — Hackathon Live Demo Script (2–3 Minutes)

This document provides an exact step-by-step walkthrough for demonstrating EvoCare to judges, clinicians, or hackathon evaluators.

---

## The Core Thesis (15 Seconds)
> "In eldercare, doctors see a 15-minute clinic snapshot every 3 months. Family caregivers see 2,000 hours of subtle shifts at home—slight stumbles, morning dizziness, confusion. 
> EvoCare is a longitudinal health memory system that bridges this gap:
> **LLM interprets. Rules constrain. Evidence proves. Memory evolves. Doctor decides.**"

---

## Act 1: The Login & Security Barrier (30 Seconds)

1. **Open the browser at `http://localhost:9000`**.
2. **Observe the Authentication Screen**:
   - Point out: EvoCare is enterprise-grade and zero-trust. Patient records cannot be viewed unauthenticated.
   - Click the **Doctor (P001)** quick-fill button (`doctor.demo`).
   - Click **Sign In**.
3. **Point out the Header**:
   - Logged in as: **Dr. Ramesh Varma, MD (DOCTOR)**
   - Patient: **Meenakshi Raman (P001, 78F, Chennai)**
   - Security pill: **READ-ONLY**, **SYNTHETIC DEMO DATA**.

---

## Act 2: Longitudinal Memory & The "Why?" Trace (60 Seconds)

1. **Patient Overview Card (6 Health Domains)**:
   - Notice the status tags: *Mobility* and *Dizziness* have warning indicators.
   - Note the domain badges: `CLINICAL RECORD` vs `CAREGIVER-REPORTED` vs `AI-DERIVED MEMORY`.
2. **Recent Changes & Living Memory**:
   - Highlight the alert: *“Intermittent outdoor support needed for ambulation”*.
   - Click the **Why?** button on this change.
   - **Show the Why Modal**:
     - Displays the exact provenance chain:
       - Memory claim: *Assisted walking observed*.
       - Evidence code: `EV-CG-002` (Caregiver observation, daughter).
       - Timestamp: Recorded on 2026-09-02.
     - Click **Inspect Raw Evidence** to open the Evidence Drawer.
     - Point out: Evidence is **IMMUTABLE** and cryptographic-style verified.
3. **Discrepancy & Conflict Analysis**:
   - Scroll to *Contextual Discrepancies*.
   - Point out: The clinical clinic note says *"Walks independently in clinic"*, but caregiver reports *"Stumbles on stairs at home"*.
   - Highlight the design choice: **EvoCare preserves the disagreement without hallucinating an artificial compromise.**

---

## Act 3: Doctor-Only Clinical Reasoning Assistant (60 Seconds)

1. **Scroll down to the Clinical Reasoning Section**:
   - Point out the red badge: **DOCTOR-ONLY CLINICAL REASONING**.
   - Caregivers and unauthorized users cannot access this engine.
2. **Demonstrate Guided Clinical Exploration**:
   - Click the quick suggestion chip: `“Why is she dizzy?”` or `“Evaluate fall risk trajectory”`.
   - Click **Analyze Trajectory**.
3. **Examine the Output Invariants**:
   - **Consideration Cards**:
     - *Status*: `POSSIBLE_CONSIDERATION` (never a definitive diagnosis).
     - *Evidence Strength*: Moderately Supported.
     - *Linked Evidence*: Clickable evidence chips (`EV-CG-003`, `EV-DR-001`).
   - **Missing Information Section**:
     - Points out what is NOT yet known: *"Orthostatic blood pressure vitals not recorded"*.
     - EvoCare adheres to: **Missing != Normal**.
   - **Mandatory Clinician Disclaimer**:
     - *"AI interprets. The treating clinician remains the sole decision-maker."*

---

## Act 4: Security & Patient Isolation Proof (20 Seconds)

1. **Test Cross-Patient Isolation**:
   - Log out by clicking **Sign out**.
   - Log in as **Caregiver** (`caregiver.demo`).
   - Notice: Caregiver view has **no access** to doctor-only Clinical Reasoning.
2. **Terminal / Verification Proof**:
   - Show `python scripts/verify_final.py` output in terminal:
   - Show `8/8 PASS` with:
     - `doctor.demo -> P002 (HTTP 403 - Forbidden)`
     - `Prompt Injection Attack intercepted and blocked (HTTP 422)`
     - `Zero database mutations verified`

---

## 30-Second Closing Pitch
> "EvoCare solves the greatest risk in clinical AI: hallucination and unauthorized action. By decoupling interpretation from decision-making and grounding every sentence in immutable evidence, we give doctors the complete picture they need—safely."
