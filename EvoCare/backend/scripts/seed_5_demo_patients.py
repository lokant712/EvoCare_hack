import os
import sys
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Adjust path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.core.database import engine, Base, SessionLocal, utc_now
import app.models  # Register all models
from app.models.patient import Patient
from app.models.baseline import Baseline
from app.models.medication import Medication
from app.models.caregiver_observation import CaregiverObservation
from app.models.memory_page import MemoryPage
from app.models.evidence import Evidence
from app.models.enums import PageType, InformationState, SourceType, EvidenceStatus
from app.models.security import User, PatientAccess, AccessRole

def seed_patients():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    patients_data = [
        {
            "patient_code": "P001",
            "name": "Meenakshi Raman",
            "email": "lokanthsrihari7@gmail.com",
            "age": 78,
            "sex": "Female",
            "location": "Chennai, Tamil Nadu",
            "status": "ACTIVE",
            "baselines": [
                ("Mobility", "Walks independently with quad cane inside home; needs assistance for distances >100m"),
                ("Falls", "History of 2 falls in past 6 months (bathroom, porch); mild right knee contusion"),
                ("Dizziness", "Postural lightheadedness upon standing rapidly; baseline BP 138/82"),
                ("Cognition", "Intact executive function (MMSE 28/30); occasional mild word-finding pause"),
                ("Nutrition", "Standard South Indian vegetarian diet, low salt; adequate hydration"),
                ("Sleep", "5-6 hours broken sleep with 2 nocturia episodes per night")
            ],
            "medications": [
                ("Metformin", "500 mg", "Twice daily with meals", "Type 2 Diabetes"),
                ("Amlodipine", "5 mg", "Once daily morning", "Hypertension"),
                ("Atorvastatin", "20 mg", "Once daily night", "Hyperlipidemia"),
                ("Paracetamol", "650 mg", "SOS for knee pain (max 2g/day)", "Osteoarthritis Knee")
            ]
        },
        {
            "patient_code": "P002",
            "name": "Ananya Sharma",
            "email": "lokanthsrihari7@gmail.com",
            "age": 64,
            "sex": "Female",
            "location": "Bengaluru, Karnataka",
            "status": "ACTIVE",
            "baselines": [
                ("Mobility", "Fully independent walker; walks 30 mins daily in park"),
                ("Falls", "No history of falls in past 12 months"),
                ("Dizziness", "Denies vertigo or presyncope; baseline BP 122/78"),
                ("Cognition", "Mild Cognitive Impairment (MoCA 24/30); forgets recent appointments"),
                ("Nutrition", "Balanced home-cooked diet; taking calcium and vitamin D supplements"),
                ("Sleep", "7 hours continuous restful sleep")
            ],
            "medications": [
                ("Donepezil", "5 mg", "Once daily at bedtime", "Mild Cognitive Impairment"),
                ("Calcium Carbonate + Vit D3", "500mg/400IU", "Once daily after breakfast", "Osteopenia"),
                ("Escitalopram", "5 mg", "Once daily morning", "Mild Anxiety")
            ]
        },
        {
            "patient_code": "P003",
            "name": "Rajesh Varma",
            "email": "lokanthsrihari7@gmail.com",
            "age": 72,
            "sex": "Male",
            "location": "Hyderabad, Telangana",
            "status": "ACTIVE",
            "baselines": [
                ("Mobility", "Uses single-point cane; dyspnea on walking >50m (NYHA Class II)"),
                ("Falls", "1 slip in garden 3 months ago; no injury"),
                ("Dizziness", "Occasional morning orthostatic dizziness; baseline BP 118/74"),
                ("Cognition", "Intact cognition (MMSE 29/30); alert and oriented x3"),
                ("Nutrition", "Strict low-sodium renal diet (<2g Na/day); fluid restriction 1.5L/day"),
                ("Sleep", "Uses 2 pillows due to orthopnea; sleeps 6 hours")
            ],
            "medications": [
                ("Sacubitril/Valsartan", "24/26 mg", "Twice daily", "Heart Failure with reduced EF"),
                ("Torsemide", "10 mg", "Once daily morning", "Fluid retention"),
                ("Spironolactone", "25 mg", "Once daily afternoon", "Heart failure"),
                ("Apixaban", "2.5 mg", "Twice daily", "Non-valvular Atrial Fibrillation")
            ]
        },
        {
            "patient_code": "P004",
            "name": "Sunita Patel",
            "email": "lokanthsrihari7@gmail.com",
            "age": 69,
            "sex": "Female",
            "location": "Ahmedabad, Gujarat",
            "status": "ACTIVE",
            "baselines": [
                ("Mobility", "Shuffling gait with resting tremor in right hand (Hoehn & Yahr Stage 2)"),
                ("Falls", "Near-miss balance loss when turning around quickly"),
                ("Dizziness", "Mild lightheadedness during levodopa peak times"),
                ("Cognition", "Mild bradyphrenia (slowness of thought) without dementia (MoCA 26/30)"),
                ("Nutrition", "Normal diet; protein intake timed 1 hr after medications"),
                ("Sleep", "Fragmented sleep with restless leg symptoms; vivid dreams")
            ],
            "medications": [
                ("Levodopa/Carbidopa", "100/25 mg", "1 tablet thrice daily (8am, 1pm, 6pm)", "Parkinson's Disease"),
                ("Pramipexole", "0.375 mg", "Once daily evening", "Restless Leg Syndrome"),
                ("Melatonin", "3 mg", "Once daily at bedtime", "REM sleep behavior disorder")
            ]
        },
        {
            "patient_code": "P005",
            "name": "Vikramaditya Rao",
            "email": "lokanthsrihari7@gmail.com",
            "age": 81,
            "sex": "Male",
            "location": "Mumbai, Maharashtra",
            "status": "ACTIVE",
            "baselines": [
                ("Mobility", "Right-sided hemiparesis; requires walker and 1-person assist for transfers"),
                ("Falls", "3 recorded falls in past year; high fall-risk precautions active"),
                ("Dizziness", "Denies true spinning; generalized postural instability"),
                ("Cognition", "Vascular Cognitive Impairment (MMSE 21/30); short-term recall deficits"),
                ("Nutrition", "Soft/pureed diet due to mild oral phase dysphagia; thickened liquids"),
                ("Sleep", "Sleep-wake inversion; frequent daytime naps, nocturnal wandering")
            ],
            "medications": [
                ("Clopidogrel", "75 mg", "Once daily morning", "Secondary Stroke Prophylaxis"),
                ("Rosuvastatin", "10 mg", "Once daily night", "Cerebrovascular Disease"),
                ("Memantine", "10 mg", "Twice daily", "Vascular Dementia"),
                ("Quetiapine", "12.5 mg", "Once SOS at bedtime", "Nocturnal agitation")
            ]
        }
    ]

    kb_roots = [
        Path(backend_dir).parent / "knowledge-base" / "Patient Wiki",
        Path(backend_dir).parent.parent / "EvoCare-Knowledge-Base" / "Patient Wiki",
        Path(backend_dir).parent / "EvoCare-Knowledge-Base" / "Patient Wiki",
    ]

    for kb_base in kb_roots:
        kb_base.mkdir(parents=True, exist_ok=True)

    for pdata in patients_data:
        code = pdata["patient_code"]
        existing = db.query(Patient).filter(Patient.patient_code == code).first()
        if not existing:
            pat = Patient(
                patient_code=code,
                name=pdata["name"],
                email=pdata["email"],
                age=pdata["age"],
                sex=pdata["sex"],
                location=pdata["location"],
                status=pdata["status"],
                is_synthetic=True
            )
            db.add(pat)
            db.commit()
            db.refresh(pat)
            print(f"Created Patient: {pat.patient_code} - {pat.name} ({pat.email})")
        else:
            existing.email = pdata["email"]
            existing.name = pdata["name"]
            existing.age = pdata["age"]
            existing.sex = pdata["sex"]
            existing.location = pdata["location"]
            db.commit()
            pat = existing
            print(f"Updated Patient: {pat.patient_code} - {pat.name} ({pat.email})")

        # Add Baselines if not present
        for cat, val in pdata["baselines"]:
            b_exist = db.query(Baseline).filter(Baseline.patient_id == pat.id, Baseline.category == cat).first()
            if not b_exist:
                db.add(Baseline(
                    patient_id=pat.id,
                    category=cat,
                    baseline_value=val,
                    information_state=InformationState.CLINICIAN_CONFIRMED
                ))

        # Add Medications if not present
        med_counter = 1
        for mname, mdose, mfreq, mind in pdata["medications"]:
            m_exist = db.query(Medication).filter(Medication.patient_id == pat.id, Medication.name == mname).first()
            if not m_exist:
                ev_code = f"EV-MED-{pat.patient_code}-{med_counter:03d}"
                med_counter += 1
                ev = db.query(Evidence).filter(Evidence.evidence_code == ev_code).first()
                if not ev:
                    ev = Evidence(
                        patient_id=pat.id,
                        evidence_code=ev_code,
                        source_type=SourceType.MEDICATION_RECORD,
                        source_id=f"RX-{pat.patient_code}",
                        observed_at=datetime.now(timezone.utc) - timedelta(days=90),
                        recorded_at=datetime.now(timezone.utc) - timedelta(days=90),
                        original_statement=f"Prescription record: {mname} {mdose}, {mfreq} for {mind}.",
                        status=EvidenceStatus.IMMUTABLE
                    )
                    db.add(ev)
                    db.flush()

                db.add(Medication(
                    patient_id=pat.id,
                    evidence_id=ev.id,
                    name=mname,
                    dose=mdose,
                    frequency=mfreq,
                    status="ACTIVE",
                    indication=mind,
                    start_date=datetime.now(timezone.utc) - timedelta(days=90)
                ))

        # Ensure Disk Wiki directory structure exists for all KB roots
        pat_dir_name = f"{pat.patient_code} {pat.name}"
        for kb_base in kb_roots:
            pat_wiki_dir = kb_base / pat_dir_name
            pat_wiki_dir.mkdir(parents=True, exist_ok=True)
            (pat_wiki_dir / "Caregiver").mkdir(exist_ok=True)
            (pat_wiki_dir / "Clinical").mkdir(exist_ok=True)
            (pat_wiki_dir / "Derived").mkdir(exist_ok=True)

            # 1. Patient Overview.md
            overview_file = pat_wiki_dir / "Patient Overview.md"
            if not overview_file.exists():
                overview_file.write_text(
                    f"# Patient Overview: {pat.name} ({pat.patient_code})\n\n"
                    f"- **Age / Sex:** {pat.age}y / {pat.sex}\n"
                    f"- **Location:** {pat.location}\n"
                    f"- **Primary Email:** {pat.email}\n"
                    f"- **Clinical Status:** {pat.status}\n"
                    f"- **Primary Physician:** Dr. Anand Rao\n"
                    f"- **Primary Caregiver:** Priya ({pat.patient_code})\n\n"
                    f"## Baseline Longitudinal Summary\n"
                    + "\n".join([f"- **{b[0]}:** {b[1]}" for b in pdata["baselines"]]) + "\n",
                    encoding="utf-8"
                )

            # 2. Clinical/Diagnoses.md
            diag_file = pat_wiki_dir / "Clinical" / "Diagnoses.md"
            if not diag_file.exists():
                diag_file.write_text(
                    f"# Active Diagnoses & Problem List: {pat.name}\n\n"
                    f"## Confirmed Clinical Conditions\n"
                    + "\n".join([f"- **{m[3]}:** Managed on {m[0]} {m[1]} ({m[2]})." for m in pdata["medications"]]) + "\n",
                    encoding="utf-8"
                )

            # 3. Clinical/Medications.md
            med_file = pat_wiki_dir / "Clinical" / "Medications.md"
            if not med_file.exists():
                med_file.write_text(
                    f"# Active Medications: {pat.name}\n\n"
                    f"| Medication | Dosage | Schedule | Indication |\n"
                    f"| :--- | :--- | :--- | :--- |\n"
                    + "\n".join([f"| **{m[0]}** | {m[1]} | {m[2]} | {m[3]} |" for m in pdata["medications"]]) + "\n",
                    encoding="utf-8"
                )

            # 4. Caregiver domain baseline markdown files
            for b_cat, b_val in pdata["baselines"]:
                cat_file = pat_wiki_dir / "Caregiver" / f"{b_cat}.md"
                if not cat_file.exists():
                    cat_file.write_text(
                        f"# Caregiver Observation Domain: {b_cat}\n"
                        f"**Patient:** {pat.name} ({pat.patient_code})\n\n"
                        f"## Baseline Assessment\n"
                        f"- **Established Baseline:** {b_val}\n\n"
                        f"## Chronological Observation Log\n"
                        f"- `[EV-CG-{pat.patient_code}-001]` Baseline established during initial comprehensive geriatric assessment.\n",
                        encoding="utf-8"
                    )

    db.commit()
    db.close()
    print("Successfully seeded all 5 demo patients with email lokanthsrihari7@gmail.com!")

if __name__ == "__main__":
    seed_patients()
