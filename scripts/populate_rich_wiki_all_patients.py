import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

ROOT_DIR = Path(__file__).resolve().parent.parent
KB_ROOT = ROOT_DIR / "EvoCare-Knowledge-Base"
BACKEND_DIR = ROOT_DIR / "EvoCare" / "backend"

sys.path.insert(0, str(BACKEND_DIR))

# Ensure directories exist
for sub in ["Caregiver", "Doctor", "Labs", "Medications", "Patient", "Medical Records"]:
    (KB_ROOT / "Raw Evidence" / sub).mkdir(parents=True, exist_ok=True)

def write_raw_evidence(code, patient_id, source_type, source_id, observed_at, statement, status="IMMUTABLE"):
    folder = "Caregiver"
    if "DR" in code or source_type == "DOCTOR":
        folder = "Doctor"
    elif "LAB" in code or source_type == "LAB":
        folder = "Labs"
    elif "MED" in code or source_type == "MEDICATION_RECORD":
        folder = "Medications"
    elif "PAT" in code or source_type == "PATIENT":
        folder = "Patient"
    
    file_path = KB_ROOT / "Raw Evidence" / folder / f"{code}.md"
    content = f"""# Evidence {code}

Patient ID: {patient_id}
Source Type: {source_type}
Source ID: {source_id}
Observed At: {observed_at}
Recorded At: {observed_at}
Original Statement:
"{statement}"
Status: {status}
"""
    file_path.write_text(content, encoding="utf-8")
    return file_path

# Clinical Profiles for All 5 Patients
PATIENTS = [
    {
        "code": "P001",
        "folder": "P001 Meenakshi Raman",
        "name": "Meenakshi Raman",
        "age": 78,
        "sex": "Female",
        "location": "Chennai, Tamil Nadu",
        "caregiver": "Priya Raman (Daughter, CG001), Suresh Raman (Son, CG002)",
        "physician": "Dr. Anand Rao, MD (Geriatric Medicine)",
        "conditions": [
            ("Type 2 Diabetes Mellitus", "E11.9", "Metformin 500mg BID", "Controlled, HbA1c 7.2%"),
            ("Essential Hypertension", "I10", "Telmisartan 40mg OD", "Mild morning orthostasis noted"),
            ("Osteoarthritis (Bilateral Knees)", "M17.0", "Paracetamol 650mg SOS", "Morning stiffness, stair difficulty"),
            ("Mild Cognitive Vulnerability", "G31.84", "Cognitive stimulation", "Intact executive function (MMSE 28/30)")
        ]
    },
    {
        "code": "P002",
        "folder": "P002 Ananya Sharma",
        "name": "Ananya Sharma",
        "age": 64,
        "sex": "Female",
        "location": "Bengaluru, Karnataka",
        "caregiver": "Rohan Sharma (Son, CG002-1), Sunita (Nurse, CG002-2)",
        "physician": "Dr. Radhika Iyer, MD (Neurology & Geriatrics)",
        "conditions": [
            ("Mild Cognitive Impairment (Amnestic)", "G31.84", "Donepezil 5mg QHS", "MoCA 24/30; short-term recall delays"),
            ("Osteopenia", "M85.80", "Calcium Carbonate + Vit D3 500mg/400IU OD", "DEXA T-score -1.8 lumbar spine"),
            ("Generalized Mild Anxiety", "F41.1", "Escitalopram 5mg OD morning", "Sleep-onset latency improved")
        ]
    },
    {
        "code": "P003",
        "folder": "P003 Rajesh Varma",
        "name": "Rajesh Varma",
        "age": 72,
        "sex": "Male",
        "location": "Hyderabad, Telangana",
        "caregiver": "Kavita Varma (Spouse, CG003-1), Amit Varma (Son, CG003-2)",
        "physician": "Dr. Sanjay Deshmukh, MD (Cardiology)",
        "conditions": [
            ("Heart Failure with Reduced Ejection Fraction (HFrEF)", "I50.22", "Sacubitril/Valsartan 24/26mg BID", "LVEF 38%, NYHA Class II"),
            ("Fluid Retention / Edema", "R60.0", "Torsemide 10mg OD morning", "Pedal edema trace, daily weight monitoring"),
            ("Non-valvular Atrial Fibrillation", "I48.0", "Apixaban 2.5mg BID", "CHA2DS2-VASc score 3"),
            ("Hypokalemia Risk", "E87.6", "Spironolactone 25mg OD afternoon", "Serum K+ 4.4 mEq/L")
        ]
    },
    {
        "code": "P004",
        "folder": "P004 Sunita Patel",
        "name": "Sunita Patel",
        "age": 69,
        "sex": "Female",
        "location": "Ahmedabad, Gujarat",
        "caregiver": "Deepak Patel (Husband, CG004-1), Meera (Home Aide, CG004-2)",
        "physician": "Dr. Arvind Mehta, MD (Movement Disorders)",
        "conditions": [
            ("Parkinson's Disease (Hoehn & Yahr Stage 2)", "G20", "Levodopa/Carbidopa 100/25mg TID", "Right-hand resting tremor, mild bradykinesia"),
            ("Restless Legs Syndrome", "G25.81", "Pramipexole 0.375mg QHS", "Evening motor restlessness relieved"),
            ("REM Sleep Behavior Disorder", "G47.52", "Melatonin 3mg QHS", "Vivid dreaming reduced")
        ]
    },
    {
        "code": "P005",
        "folder": "P005 Vikramaditya Rao",
        "name": "Vikramaditya Rao",
        "age": 81,
        "sex": "Male",
        "location": "Mumbai, Maharashtra",
        "caregiver": "Lakshmi Rao (Daughter, CG005-1), Naresh (Care Assistant, CG005-2)",
        "physician": "Dr. Farhan Qureshi, MD (Geriatric Neuro-Rehab)",
        "conditions": [
            ("Ischemic Stroke with Right Hemiparesis", "I69.351", "Clopidogrel 75mg OD + Rosuvastatin 10mg QHS", "Uses hemi-walker; 1-person transfer assist"),
            ("Vascular Cognitive Impairment", "F01.50", "Memantine 10mg BID", "MMSE 21/30; executive & processing slowing"),
            ("High Fall Risk", "R29.6", "Physical Therapy 3x/week", "Morse Fall Scale 65 (High Risk)"),
            ("Oropharyngeal Dysphagia (Mild)", "R13.10", "Level 4 Pureed diet, Level 2 mildly thick fluids", "Speech Therapy monitoring")
        ]
    }
]

def generate_patient_wiki(p):
    code = p["code"]
    name = p["name"]
    folder = p["folder"]
    pat_dir = KB_ROOT / "Patient Wiki" / folder
    
    (pat_dir / "Caregiver").mkdir(parents=True, exist_ok=True)
    (pat_dir / "Clinical").mkdir(parents=True, exist_ok=True)
    (pat_dir / "Derived").mkdir(parents=True, exist_ok=True)
    
    # 1. Patient Overview.md
    overview_md = f"""# Patient Overview: {name} ({code})

> **LIVING CLINICAL RECORD & LONGITUDINAL MEMORY PROFILE**  
> System: EvoCare Gericare Health Memory Layer | Architecture: Multi-Agent Clinical Core

---

## Demographic & Administrative Profile
- **Full Legal Name:** {name}
- **Patient Identifier:** `{code}`
- **Age / Biological Sex:** {p["age"]} Years / {p["sex"]}
- **Primary Residential Location:** {p["location"]}
- **Primary Attending Physician:** {p["physician"]}
- **Family Caregiver Contact:** {p["caregiver"]}
- **Clinical Monitoring Status:** ACTIVE LONGITUDINAL SURVEILLANCE

---

## Active Problem List & Diagnoses
| Condition | ICD-10 | Primary Management | Clinical Status | Evidence |
| :--- | :--- | :--- | :--- | :--- |
"""
    med_ev_idx = 1
    for cond, icd, rx, status in p["conditions"]:
        ev_c = f"EV-DR-{code}-{med_ev_idx:03d}"
        write_raw_evidence(ev_c, code, "DOCTOR", "DR001", "2026-08-15 10:00:00", f"Clinical diagnosis confirmed: {cond} ({icd}). Strategy: {rx}.")
        overview_md += f"| **{cond}** | `{icd}` | {rx} | {status} | [[Raw Evidence/Doctor/{ev_c}|{ev_c}]] |\n"
        med_ev_idx += 1

    overview_md += f"""
---

## Navigation & Wiki Sub-Domains
- **[[Caregiver/Mobility|Caregiver Mobility Observations]]** — Functional ambulation, sit-to-stand, and assistive device usage
- **[[Caregiver/Falls|Caregiver Falls & Near-Miss Logs]]** — Incident reports, environmental factors, and fall trajectory
- **[[Caregiver/Dizziness|Caregiver Dizziness & Orthostasis]]** — Postural lightheadedness, timing relative to meds, and hydration
- **[[Caregiver/Cognition|Caregiver Cognitive & Behavioral Logs]]** — Memory recall, orientation, confusion, and lucidity
- **[[Caregiver/Nutrition|Caregiver Nutrition & Hydration Logs]]** — Meal completion, fluid intake, and dietary adherence
- **[[Caregiver/Sleep|Caregiver Sleep & Nighttime Patterns]]** — Sleep duration, fragmentation, nocturia, and restfulness
- **[[Clinical/Diagnoses|Active Diagnoses & ICD-10 Registry]]** — Formal clinician-verified problem list
- **[[Clinical/Medications|Medication Regimen & Reconciliation]]** — Active pharmacology, dosing, and schedule
- **[[Clinical/Doctor Assessments|Doctor Assessments]]** — Longitudinal geriatric clinical encounter notes
- **[[Derived/Baseline|Established Longitudinal Baselines]]** — Clinician-validated behavioral and physiological norms
- **[[Derived/Conflicts|Derived Evidence Conflicts]]** — Cross-stream reconciliation and discrepancy tracking
- **[[Derived/Patient Memory Summary|Synthesized Patient Memory Summary]]** — Automated temporal clinical memory synthesis
"""
    (pat_dir / "Patient Overview.md").write_text(overview_md, encoding="utf-8")

    # 2. Caregiver Logs (9 Domains)
    caregiver_domains = [
        ("Mobility", "Functional ambulation, gait velocity, balance, and assistive support requirements."),
        ("Falls", "Documented falls, slips, near-miss stumbles, and environmental hazards."),
        ("Dizziness", "Lightheadedness, vertigo episodes, postural transitions, and timing relative to morning medications."),
        ("Cognition", "Memory recall, orientation to time/place, word-finding, task execution, and lucidity."),
        ("Nutrition", "Appetite, caloric intake, dysphagia observations, meal completion, and hydration volume."),
        ("Sleep", "Nocturnal sleep latency, nighttime awakenings, nocturia episodes, and daytime somnolence."),
        ("Pain", "Musculoskeletal discomfort, joint stiffness, localized pain scores (0-10), and relief post-analgesics."),
        ("Behavior", "Mood stability, emotional affect, social engagement, agitation, or sunsetting signs."),
        ("Medication Adherence", "Compliance logs, timing verification, missed dosages, and pill-taking assistance.")
    ]

    for dom, desc in caregiver_domains:
        ev1 = f"EV-CG-{code}-{dom[:3].upper()}-001"
        ev2 = f"EV-CG-{code}-{dom[:3].upper()}-002"
        ev3 = f"EV-CG-{code}-{dom[:3].upper()}-003"
        ev4 = f"EV-CG-{code}-{dom[:3].upper()}-004"
        
        stmt1 = f"Baseline status for {dom.lower()}: Patient exhibits standard baseline functional capacity."
        stmt2 = f"Mid-week check for {dom.lower()}: Stable condition observed during morning routine."
        stmt3 = f"Caregiver logged slight variance in {dom.lower()}; patient was monitored closely."
        stmt4 = f"Follow-up observation: Patient recovered to baseline {dom.lower()} with family assistance."
        
        write_raw_evidence(ev1, code, "CAREGIVER", "CG001", "2026-08-20 08:30:00", stmt1)
        write_raw_evidence(ev2, code, "CAREGIVER", "CG001", "2026-08-27 12:15:00", stmt2)
        write_raw_evidence(ev3, code, "CAREGIVER", "CG002", "2026-09-04 17:45:00", stmt3)
        write_raw_evidence(ev4, code, "CAREGIVER", "CG001", "2026-09-09 09:00:00", stmt4)

        cg_md = f"""# Caregiver Observation Log: {dom}

> **PATIENT RECORD: {name} ({code})**  
> Domain: `{dom}` | Sub-system: Caregiver Observation Stream

---

## Domain Overview
{desc}

---

## Established Baseline
- **Clinical Baseline:** Clinician-verified baseline profile active for {name}.
*Evidence Reference: [[Raw Evidence/Doctor/EV-DR-{code}-001|EV-DR-{code}-001]], [[Derived/Baseline|Derived Baseline Profile]]*

---

## Chronological Caregiver Observations

| Date | Observer | Verbatim Statement | Functional Interpretation | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-20** | Family Caregiver | *"{stmt1}"* | Baseline functional status logged | [[Raw Evidence/Caregiver/{ev1}|{ev1}]] |
| **2026-08-27** | Family Caregiver | *"{stmt2}"* | Stable longitudinal maintenance | [[Raw Evidence/Caregiver/{ev2}|{ev2}]] |
| **2026-09-04** | Care Assistant | *"{stmt3}"* | Transient sub-acute fluctuation | [[Raw Evidence/Caregiver/{ev3}|{ev3}]] |
| **2026-09-09** | Primary Caregiver | *"{stmt4}"* | Recovery to stable baseline trajectory | [[Raw Evidence/Caregiver/{ev4}|{ev4}]] |

---

## Related Longitudinal Memory Links
- [[Derived/{dom} Trends|{dom} Temporal Trend Analysis]]
- [[Derived/Baseline|Patient Longitudinal Baseline]]
- [[Derived/Conflicts|Cross-Stream Discrepancy Checks]]
- [[Patient Overview|Back to Patient Overview]]
"""
        (pat_dir / "Caregiver" / f"{dom}.md").write_text(cg_md, encoding="utf-8")

    # 3. Clinical Notes (5 files)
    # Diagnoses.md
    diag_md = f"""# Active Diagnoses & Problem List: {name} ({code})

> **CLINICAL MASTER REGISTRY** | Verifier: {p["physician"]}

---

## Confirmed Clinical Conditions
"""
    for cond, icd, rx, status in p["conditions"]:
        diag_md += f"- **{cond} (`{icd}`):** {status}. Managed with {rx}.\n"
    diag_md += f"\n*Referenced in [[Patient Overview|Patient Overview]] and [[Derived/Baseline|Derived Baseline]].*\n"
    (pat_dir / "Clinical" / "Diagnoses.md").write_text(diag_md, encoding="utf-8")

    # Medications.md
    med_md = f"""# Active Medication Regimen: {name} ({code})

> **RECONCILED PHARMACOTHERAPY PROFILE** | Updated: 2026-09-01

| Medication Name | Dosage | Schedule | Clinical Indication | Evidence Link |
| :--- | :--- | :--- | :--- | :--- |
"""
    for i, (cond, icd, rx, status) in enumerate(p["conditions"], start=1):
        m_ev = f"EV-MED-{code}-{i:03d}"
        write_raw_evidence(m_ev, code, "MEDICATION_RECORD", f"RX-{code}", "2026-08-15 09:00:00", f"Rx Active: {rx} for {cond}.")
        med_md += f"| **{rx.split(' ')[0]}** | {' '.join(rx.split(' ')[1:3])} | {' '.join(rx.split(' ')[3:]) or 'Daily'} | {cond} | [[Raw Evidence/Medications/{m_ev}|{m_ev}]] |\n"
    (pat_dir / "Clinical" / "Medications.md").write_text(med_md, encoding="utf-8")

    # Doctor Assessments.md
    dr_ev1 = f"EV-DR-{code}-ENC-001"
    dr_ev2 = f"EV-DR-{code}-ENC-002"
    write_raw_evidence(dr_ev1, code, "DOCTOR", "DR001", "2026-08-15 11:30:00", f"Comprehensive Geriatric Assessment encounter note for {name}.")
    write_raw_evidence(dr_ev2, code, "DOCTOR", "DR001", "2026-09-01 14:00:00", f"Longitudinal follow-up assessment and medication review for {name}.")
    
    dr_md = f"""# Doctor Clinical Assessments: {name} ({code})

> **ATTENDING PHYSICIAN ENCOUNTER NOTES** | {p["physician"]}

---

### Encounter 1: Comprehensive Initial Geriatric Assessment (2026-08-15)
- **Subjective:** Patient accompanied by family. Routine health review and functional appraisal.
- **Objective:** Vitals stable. Systemic examination reviewed. Cognitive & motor screening conducted.
- **Assessment:** Geriatric multi-domain stability with ongoing home-based monitoring.
- **Plan:** Continue active prescriptions. Caregiver to track daily symptoms via EvoCare.
*Evidence Citation: [[Raw Evidence/Doctor/{dr_ev1}|{dr_ev1}]]*

---

### Encounter 2: Longitudinal Follow-up & Memory Review (2026-09-01)
- **Subjective:** Caregiver logs reviewed over previous fortnight.
- **Objective:** Patient oriented and functionally responsive.
- **Assessment:** Regimen well-tolerated. No acute red flags identified.
*Evidence Citation: [[Raw Evidence/Doctor/{dr_ev2}|{dr_ev2}]]*
"""
    (pat_dir / "Clinical" / "Doctor Assessments.md").write_text(dr_md, encoding="utf-8")

    # Laboratory History.md
    lab_ev1 = f"EV-LAB-{code}-001"
    lab_ev2 = f"EV-LAB-{code}-002"
    write_raw_evidence(lab_ev1, code, "LAB", "LAB001", "2026-08-16 08:00:00", f"Comprehensive Metabolic Panel & CBC for {name}.")
    write_raw_evidence(lab_ev2, code, "LAB", "LAB001", "2026-09-02 08:30:00", f"Follow-up Serum Electrolytes & Renal Function Panel for {name}.")

    lab_md = f"""# Laboratory & Diagnostic History: {name} ({code})

> **DIAGNOSTIC ARCHIVE & TREND LOG**

| Test Date | Diagnostic Panel | Key Parameters | Clinician Interpretation | Evidence ID |
| :--- | :--- | :--- | :--- | :--- |
| **2026-08-16** | Comprehensive Metabolic Panel | eGFR >65, Creatinine 0.9 mg/dL, Fasting Glucose 118 | Stable baseline organ function | [[Raw Evidence/Labs/{lab_ev1}|{lab_ev1}]] |
| **2026-09-02** | Serum Electrolytes & Renal Panel | K+ 4.3 mEq/L, Na+ 139 mEq/L, Urea 28 mg/dL | Normal range; safe for ongoing therapy | [[Raw Evidence/Labs/{lab_ev2}|{lab_ev2}]] |
"""
    (pat_dir / "Clinical" / "Laboratory History.md").write_text(lab_md, encoding="utf-8")

    # Medical History.md
    hist_md = f"""# Past Medical & Surgical History: {name} ({code})

> **LONGITUDINAL HEALTH RECORD BACKGROUND**

- **Established Chronic Conditions:** {', '.join([c[0] for c in p['conditions']])}
- **Surgical History:** Non-contributory major trauma; elective procedures uneventful.
- **Allergies:** No known drug allergies (NKDA).
- **Immunization Status:** Up-to-date with annual Influenza and pneumococcal conjugate vaccines.
"""
    (pat_dir / "Clinical" / "Medical History.md").write_text(hist_md, encoding="utf-8")

    # 4. Derived Synthesis (9 files)
    # Baseline.md
    base_md = f"""# Longitudinal Derived Baseline: {name} ({code})

> **CLINICIAN-CONFIRMED MULTI-DOMAIN BASELINE PROFILE**

| Domain | Established Baseline Functional Capacity | Confirmation Status | Supporting Evidence |
| :--- | :--- | :--- | :--- |
| **Mobility** | Independent indoor ambulation; stable functional gait | Clinician Confirmed | [[Raw Evidence/Doctor/{dr_ev1}|{dr_ev1}]] |
| **Falls** | No recurrent unassisted falls in prior surveillance cycle | Clinician Confirmed | [[Raw Evidence/Caregiver/EV-CG-{code}-FAL-001|EV-CG-{code}-FAL-001]] |
| **Dizziness** | Occasional mild postural lightheadedness on rapid rising | Clinician Confirmed | [[Raw Evidence/Caregiver/EV-CG-{code}-DIZ-001|EV-CG-{code}-DIZ-001]] |
| **Cognition** | Age-appropriate cognitive performance; intact daily living activities | Clinician Confirmed | [[Raw Evidence/Doctor/{dr_ev1}|{dr_ev1}]] |
| **Nutrition** | Regular balanced oral diet; adequate daily fluid intake | Clinician Confirmed | [[Raw Evidence/Caregiver/EV-CG-{code}-NUT-001|EV-CG-{code}-NUT-001]] |
| **Sleep** | 6-7 hours nightly rest with manageable sleep transitions | Clinician Confirmed | [[Raw Evidence/Caregiver/EV-CG-{code}-SLE-001|EV-CG-{code}-SLE-001]] |
"""
    (pat_dir / "Derived" / "Baseline.md").write_text(base_md, encoding="utf-8")

    # Trend Files (Mobility, Falls, Dizziness, Cognition, Nutrition, Sleep)
    trends = [
        ("Mobility Trends", "Mobility", "Stable functional trajectory with consistent daily ambulation logs."),
        ("Falls Trends", "Falls", "Low-to-moderate longitudinal fall index; safety precautions maintained."),
        ("Dizziness Trends", "Dizziness", "Postural symptoms well-controlled with medication timing adjustments."),
        ("Cognition Trends", "Cognition", "Cognitive clarity maintained; no acute delirium or rapid decline signals."),
        ("Nutrition Trends", "Nutrition", "Caloric and fluid goals achieved consistently across monitoring weeks."),
        ("Sleep Trends", "Sleep", "Restful sleep duration averaging 6.5 hours per 24-hour cycle.")
    ]
    for tname, tdom, tdesc in trends:
        t_md = f"""# Derived Longitudinal Trends: {tdom}

> **PATIENT RECORD: {name} ({code})** | Automated Temporal Analysis

---

## Trend Summary
{tdesc}

---

## Temporal Trajectory Analysis
- **Baseline Comparison:** Aligned with baseline parameters established on 2026-08-15.
- **30-Day Variance:** Minimal clinically actionable deviation noted.
- **Associated Evidence Points:**
  - [[Raw Evidence/Caregiver/EV-CG-{code}-{tdom[:3].upper()}-001|EV-CG-{code}-{tdom[:3].upper()}-001]] (Initial)
  - [[Raw Evidence/Caregiver/EV-CG-{code}-{tdom[:3].upper()}-004|EV-CG-{code}-{tdom[:3].upper()}-004]] (Recent)

---

## Recommended Clinical Action
Continue active observation cadence with regular caregiver check-ins.
"""
        (pat_dir / "Derived" / f"{tname}.md").write_text(t_md, encoding="utf-8")

    # Conflicts.md
    conf_md = f"""# Cross-Stream Discrepancy & Conflict Analysis: {name} ({code})

> **AUTOMATED DISCREPANCY RECONCILIATION ENGINE**

---

## Active Discrepancies
*No unresolved critical diagnostic conflicts detected between caregiver logs and clinician encounter assessments.*

---

## Historical Reconciliations
- **Medication Timing vs Symptom Perception:** Caregiver reported occasional tiredness; clinician reviewed and confirmed non-pathological post-prandial rest.
- **Status:** RECONCILED / CLINICIAN_CONFIRMED.
"""
    (pat_dir / "Derived" / "Conflicts.md").write_text(conf_md, encoding="utf-8")

    # Patient Memory Summary.md
    mem_summary_md = f"""# Synthesized Patient Memory Summary: {name} ({code})

> **COMPREHENSIVE LONGITUDINAL HEALTH MEMORY LAYER**

---

## Executive Summary
Patient {name} ({code}), {p["age"]}yo {p["sex"]}, managed for {', '.join([c[0] for c in p['conditions']])}. 
Longitudinal health memory reflects robust home caregiver documentation paired with scheduled geriatric specialty oversight. All active evidence chains are anchored to immutable provenance records.

---

## Key Clinical Highlights
1. **Pharmacotherapy:** Verified active medications compliant with renal and cardiovascular safety profiles.
2. **Functional Independence:** Stable baseline ambulation and daily activity performance.
3. **Safety Index:** Proactive caregiver logging prevents unmonitored symptom progression.

---

## Linked Records
- [[Patient Overview|Patient Overview]]
- [[Derived/Baseline|Clinician Baseline]]
- [[Clinical/Diagnoses|Diagnoses List]]
- [[Clinical/Medications|Active Medications]]
- [[Derived/Conflicts|Conflict Tracker]]
"""
    (pat_dir / "Derived" / "Patient Memory Summary.md").write_text(mem_summary_md, encoding="utf-8")

print("Generating rich, complete living wikis for all 5 patients...")
for pat in PATIENTS:
    generate_patient_wiki(pat)
    print(f"Generated complete wiki set for {pat['code']} - {pat['name']}")

print("\nAll 5 demo patients now have full, multi-tier Obsidian Markdown knowledge bases!")
