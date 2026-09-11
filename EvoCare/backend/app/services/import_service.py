import os
import re
from datetime import datetime
from pathlib import Path
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.enums import SourceType, InformationState, EvidenceStatus, ConflictStatus, PageType
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.observation import Observation
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.memory_page import MemoryPage

class ImportService:
    @staticmethod
    def parse_evidence_file(file_path: Path) -> dict:
        content = file_path.read_text(encoding="utf-8")
        
        ev_code_m = re.search(r"#\s*Evidence\s+([A-Z0-9\-]+)", content)
        ev_code = ev_code_m.group(1).strip() if ev_code_m else file_path.stem

        patient_id_m = re.search(r"Patient ID:\s*([A-Z0-9\-]+)", content)
        patient_code = patient_id_m.group(1).strip() if patient_id_m else "P001"

        source_type_m = re.search(r"Source Type:\s*([A-Z_]+)", content)
        source_type_str = source_type_m.group(1).strip() if source_type_m else "CAREGIVER"
        try:
            source_type = SourceType(source_type_str)
        except ValueError:
            source_type = SourceType.CAREGIVER

        source_id_m = re.search(r"Source ID:\s*([A-Za-z0-9_\-]+)", content)
        source_id = source_id_m.group(1).strip() if source_id_m else "UNKNOWN"

        observed_at_m = re.search(r"Observed At:\s*([0-9\-]+)", content)
        observed_at_str = observed_at_m.group(1).strip() if observed_at_m else "2026-08-01"
        try:
            observed_at = datetime.strptime(observed_at_str, "%Y-%m-%d")
        except ValueError:
            observed_at = datetime(2026, 8, 1)

        recorded_at_m = re.search(r"Recorded At:\s*([0-9\-]+)", content)
        recorded_at_str = recorded_at_m.group(1).strip() if recorded_at_m else observed_at_str
        try:
            recorded_at = datetime.strptime(recorded_at_str, "%Y-%m-%d")
        except ValueError:
            recorded_at = observed_at

        # Statement
        stmt_m = re.search(r"Original Statement:\s*\n+([^\n].*?)(?=\n\s*Status:|\Z)", content, re.DOTALL)
        if stmt_m:
            statement = stmt_m.group(1).strip().strip('"').strip()
        else:
            statement = content.strip()

        return {
            "evidence_code": ev_code,
            "patient_code": patient_code,
            "source_type": source_type,
            "source_id": source_id,
            "observed_at": observed_at,
            "recorded_at": recorded_at,
            "original_statement": statement,
            "status": EvidenceStatus.IMMUTABLE
        }

    @classmethod
    def import_all(cls, db: Session, kb_dir: str = None) -> dict:
        kb_path = Path(kb_dir or settings.KNOWLEDGE_BASE_DIR)
        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge Base directory not found at: {kb_path}")

        # 1. Create or get synthetic patient
        patient = db.query(Patient).filter(Patient.patient_code == "P001").first()
        if not patient:
            patient = Patient(
                patient_code="P001",
                name="Meenakshi Raman",
                age=78,
                sex="Female",
                location="Chennai, Tamil Nadu",
                status="ACTIVE",
                is_synthetic=True
            )
            db.add(patient)
            db.flush()

        # 2. Import Raw Evidence
        evidence_dir = kb_path / "Raw Evidence"
        evidence_map = {}  # code -> Evidence model

        for root, dirs, files in os.walk(evidence_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    file_path = Path(root) / file_name
                    ev_data = cls.parse_evidence_file(file_path)
                    
                    ev = db.query(Evidence).filter(Evidence.evidence_code == ev_data["evidence_code"]).first()
                    if not ev:
                        ev = Evidence(
                            patient_id=patient.id,
                            evidence_code=ev_data["evidence_code"],
                            source_type=ev_data["source_type"],
                            source_id=ev_data["source_id"],
                            observed_at=ev_data["observed_at"],
                            recorded_at=ev_data["recorded_at"],
                            original_statement=ev_data["original_statement"],
                            status=ev_data["status"]
                        )
                        db.add(ev)
                        db.flush()
                    evidence_map[ev.evidence_code] = ev

        # 3. Create Caregiver Observations
        category_map = {
            "EV-CG-001": ("mobility", "normal"),
            "EV-CG-002": ("cognition", "glasses misplacement"),
            "EV-CG-003": ("nutrition", "good intake"),
            "EV-CG-004": ("behavior", "good mood"),
            "EV-CG-005": ("sleep", "7 hours normal"),
            "EV-CG-006": ("mobility", "unsteady on chair rise"),
            "EV-CG-007": ("pain", "knee pain after walking"),
            "EV-CG-008": ("dizziness", "transient dizziness"),
            "EV-CG-009": ("medication_adherence", "morning meds assisted"),
            "EV-CG-010": ("dizziness", "dizziness follow-up"),
            "EV-CG-011": ("mobility", "holding dining table"),
            "EV-CG-012": ("nutrition", "left half lunch"),
            "EV-CG-013": ("cognition", "repeated question in evening"),
            "EV-CG-014": ("mobility", "normal morning walk"),
            "EV-CG-015": ("pain", "mild knee pain"),
            "EV-CG-016": ("behavior", "quiet in afternoon"),
            "EV-CG-017": ("sleep", "woke up 3 times"),
            "EV-CG-018": ("dizziness", "postural morning dizziness"),
            "EV-CG-019": ("nutrition", "ate less at dinner"),
            "EV-CG-020": ("medication_adherence", "evening med reminder"),
            "EV-CG-021": ("mobility", "needed arm support outside"),
            "EV-CG-022": ("cognition", "confused about day"),
            "EV-CG-023": ("nutrition", "only few bites"),
            "EV-CG-024": ("sleep", "poor sleep"),
            "EV-CG-025": ("mobility", "slower walking"),
            "EV-CG-026": ("cognition", "normal morning chatting"),
            "EV-CG-027": ("pain", "no knee pain"),
            "EV-CG-028": ("dizziness", "evening dizziness"),
            "EV-CG-029": ("nutrition", "appetite better"),
            "EV-CG-030": ("behavior", "laughing and watching tv"),
            "EV-CG-031": ("near_fall", "almost fell near bathroom"),
            "EV-CG-032": ("dizziness", "dizzy and held wall"),
            "EV-CG-033": ("medication_adherence", "weekly pill organizer"),
            "EV-CG-034": ("cognition", "confused around dinner"),
            "EV-CG-035": ("sleep", "slept better"),
            "EV-CG-036": ("mobility", "support bedroom to kitchen"),
            "EV-CG-037": ("nutrition", "ate 3/4 of meal"),
            "EV-CG-038": ("pain", "knee hurt outside"),
            "EV-CG-039": ("behavior", "frustrated with slow walk"),
            "EV-CG-040": ("mobility", "walking better without support"),
            "EV-CG-041": ("cognition", "recognized everyone talking normally"),
            "EV-CG-042": ("medication_adherence", "meds on time"),
            "EV-CG-043": ("dizziness", "ambiguous dizziness"),
            "EV-CG-044": ("general_status", "ambiguous weakness"),
            "EV-CG-045": ("cognition", "ambiguous confusion"),
            "EV-CG-046": ("nutrition", "ambiguous intake"),
            "EV-CG-047": ("behavior", "ambiguous demeanor")
        }

        for ev_code, ev in evidence_map.items():
            if ev.source_type == SourceType.CAREGIVER:
                cat, subcat = category_map.get(ev_code, ("other", "general"))
                is_ambiguous = ev_code in ("EV-CG-043", "EV-CG-044", "EV-CG-045", "EV-CG-046", "EV-CG-047", "EV-CG-008", "EV-CG-010")
                attrs = {
                    "subcategory": subcat,
                    "clarification_required": is_ambiguous
                }
                if is_ambiguous:
                    attrs["missing_fields"] = ["severity", "duration", "trigger"]
                if ev_code == "EV-CG-031" or "almost fell" in (ev.original_statement or "").lower():
                    attrs["classification"] = "NEAR_FALL"
                    attrs["ground_impact"] = False
                if ev_code == "EV-CG-040":
                    attrs["improvement"] = True

                existing_cg = db.query(CaregiverObservation).filter(CaregiverObservation.evidence_id == ev.id).first()
                if not existing_cg:
                    cg_obs = CaregiverObservation(
                        patient_id=patient.id,
                        evidence_id=ev.id,
                        caregiver_id=ev.source_id,
                        category=cat,
                        observation_text=ev.original_statement,
                        attributes=attrs,
                        observed_at=ev.observed_at,
                        information_state=InformationState.OBSERVED
                    )
                    db.add(cg_obs)
                else:
                    existing_attrs = dict(existing_cg.attributes or {})
                    existing_attrs.update(attrs)
                    existing_cg.attributes = existing_attrs

                # Also populate general Observation table
                existing_obs = db.query(Observation).filter(Observation.evidence_id == ev.id).first()
                if not existing_obs:
                    cat, subcat = category_map.get(ev_code, ("caregiver_observation", "general"))
                    is_ambiguous = ev_code in ("EV-CG-043", "EV-CG-044", "EV-CG-045", "EV-CG-046", "EV-CG-047")
                    obs = Observation(
                        patient_id=patient.id,
                        evidence_id=ev.id,
                        category=cat,
                        status=InformationState.OBSERVED,
                        observed_at=ev.observed_at,
                        clarification_required=is_ambiguous
                    )
                    db.add(obs)

        # 4. Doctor Records
        for ev_code in ["EV-DR-001", "EV-DR-002", "EV-DR-003", "EV-DR-004", "EV-DR-005"]:
            if ev_code in evidence_map:
                ev = evidence_map[ev_code]
                existing_dr = db.query(DoctorRecord).filter(DoctorRecord.evidence_id == ev.id).first()
                if not existing_dr:
                    dr_rec = DoctorRecord(
                        patient_id=patient.id,
                        evidence_id=ev.id,
                        doctor_id=ev.source_id,
                        record_type="consultation" if ev_code in ("EV-DR-001", "EV-DR-003", "EV-DR-005") else "follow_up",
                        content=ev.original_statement,
                        observed_at=ev.observed_at
                    )
                    db.add(dr_rec)

        # 5. Medications
        med_specs = [
            ("EV-MED-001", "Metformin", "500 mg", "twice daily", "ACTIVE", "Type 2 Diabetes Mellitus"),
            ("EV-MED-002", "Amlodipine", "5 mg", "once daily", "ACTIVE", "Essential Hypertension"),
            ("EV-MED-003", "Atorvastatin", "10 mg", "once nightly", "ACTIVE", "Hyperlipidemia"),
            ("EV-MED-004", "Paracetamol", "500 mg", "PRN (as needed)", "ACTIVE", "Bilateral Knee Osteoarthritis Pain"),
        ]
        for ev_code, name, dose, freq, status, ind in med_specs:
            if ev_code in evidence_map:
                ev = evidence_map[ev_code]
                existing_med = db.query(Medication).filter(Medication.evidence_id == ev.id).first()
                if not existing_med:
                    med = Medication(
                        patient_id=patient.id,
                        evidence_id=ev.id,
                        name=name,
                        dose=dose,
                        frequency=freq,
                        status=status,
                        indication=ind,
                        start_date=ev.observed_at
                    )
                    db.add(med)

        # 6. Labs
        lab_specs = [
            ("EV-LAB-001", "Glycemic & Renal Panel", [
                ("HbA1c", "7.1", "%", "< 7.5%"),
                ("Serum Creatinine", "0.9", "mg/dL", "0.5 - 1.1 mg/dL"),
                ("Serum Sodium", "138", "mmol/L", "135 - 145 mmol/L"),
                ("Serum Potassium", "4.3", "mmol/L", "3.5 - 5.0 mmol/L"),
                ("Hemoglobin", "12.4", "g/dL", "12.0 - 15.5 g/dL")
            ]),
            ("EV-LAB-002", "Glycemic & Renal Panel", [
                ("HbA1c", "7.3", "%", "< 7.5%"),
                ("Serum Creatinine", "0.9", "mg/dL", "0.5 - 1.1 mg/dL"),
                ("Serum Sodium", "139", "mmol/L", "135 - 145 mmol/L"),
                ("Serum Potassium", "4.2", "mmol/L", "3.5 - 5.0 mmol/L"),
                ("Hemoglobin", "12.2", "g/dL", "12.0 - 15.5 g/dL")
            ]),
            ("EV-LAB-003", "Glycemic & Renal Panel", [
                ("HbA1c", "7.4", "%", "< 7.5%"),
                ("Serum Creatinine", "0.9", "mg/dL", "0.5 - 1.1 mg/dL"),
                ("Serum Sodium", "137", "mmol/L", "135 - 145 mmol/L"),
                ("Serum Potassium", "4.3", "mmol/L", "3.5 - 5.0 mmol/L"),
                ("Hemoglobin", "12.1", "g/dL", "12.0 - 15.5 g/dL")
            ])
        ]
        for ev_code, panel, biomarkers in lab_specs:
            if ev_code in evidence_map:
                ev = evidence_map[ev_code]
                for t_name, val, unit, ref in biomarkers:
                    existing_l = db.query(LabRecord).filter(
                        LabRecord.evidence_id == ev.id,
                        LabRecord.test_name == t_name
                    ).first()
                    if not existing_l:
                        lab_rec = LabRecord(
                            patient_id=patient.id,
                            evidence_id=ev.id,
                            test_panel=panel,
                            test_name=t_name,
                            value=val,
                            unit=unit,
                            reference_range=ref,
                            observed_at=ev.observed_at
                        )
                        db.add(lab_rec)

        # 7. Baselines
        baseline_specs = [
            ("mobility", "Independently Mobile without routine walking aids", ["EV-PAT-002", "EV-DR-001", "EV-DR-003", "EV-DR-005"]),
            ("nutrition", "Generally Good Appetite, regularly completes full meals", ["EV-PAT-003", "EV-CG-003"]),
            ("sleep", "~7 Hours nocturnal sleep with occasional single waking", ["EV-CG-005"]),
            ("cognition", "Occasional benign forgetfulness; fully oriented to family; NO dementia diagnosis", ["EV-PAT-004", "EV-DR-001", "EV-DR-003"]),
            ("mood_behavior", "Calm, cheerful, socially active with family and grandchildren", ["EV-CG-004", "EV-CG-030"]),
            ("pain", "Intermittent mild bilateral knee discomfort on exertion", ["EV-DR-001", "EV-CG-015"]),
            ("dizziness", "No established persistent dizziness pattern historically", ["EV-DR-001", "EV-DR-005"]),
            ("falls", "One historical slip ~8 months prior (Jan 2026) without fracture", ["EV-PAT-001", "EV-MR-002"]),
            ("medication_management", "Takes medications reliably with family pillbox prep and reminders", ["EV-DR-005", "EV-CG-033"])
        ]
        for cat, val, ev_codes in baseline_specs:
            b = db.query(Baseline).filter(Baseline.patient_id == patient.id, Baseline.category == cat).first()
            if not b:
                b = Baseline(
                    patient_id=patient.id,
                    category=cat,
                    baseline_value=val,
                    information_state=InformationState.HISTORICAL
                )
                for code in ev_codes:
                    if code in evidence_map:
                        b.supporting_evidences.append(evidence_map[code])
                db.add(b)

        # 8. Derived Patterns
        pattern_specs = [
            ("mobility", "Possible mobility deviation from baseline with partial improvement",
             "Caregiver observations describe progressive unsteadiness, furniture cruising, arm assistance, and a near-fall on 2026-09-06, followed by partial recovery with independent indoor walking on 2026-09-09.",
             ["EV-DR-005", "EV-CG-001", "EV-CG-006", "EV-CG-011", "EV-CG-014", "EV-CG-021", "EV-CG-025", "EV-CG-031", "EV-CG-036", "EV-CG-040"]),
            ("cognition", "Intermittent evening confusion with preserved morning clarity",
             "Caregiver logs show transient evening confusion notes on 2026-08-29, 2026-09-02, and 2026-09-07, alternating with clear morning communication and full family recognition on 2026-09-09. No dementia diagnosed.",
             ["EV-DR-005", "EV-CG-002", "EV-CG-013", "EV-CG-022", "EV-CG-026", "EV-CG-034", "EV-CG-041"]),
            ("nutrition", "Transient dietary intake reduction followed by appetite recovery",
             "Caregivers reported reduced food intake between 2026-08-28 and 2026-09-03, followed by clear appetite improvement on 2026-09-05 and 2026-09-08 (~75% intake).",
             ["EV-CG-003", "EV-CG-012", "EV-CG-019", "EV-CG-023", "EV-CG-029", "EV-CG-037"]),
            ("sleep", "Fluctuating sleep fragmentation with subsequent restorative sleep",
             "Intermittent nocturnal sleep fragmentation recorded in late August / early September with recovery on 2026-09-07.",
             ["EV-CG-005", "EV-CG-017", "EV-CG-024", "EV-CG-035"]),
            ("dizziness", "Repeated caregiver-reported dizziness with postural characteristics",
             "Recurrent episodic dizziness observed between 2026-08-25 and 2026-09-06, including an episode upon getting out of bed that resolved upon sitting. Cause unknown.",
             ["EV-CG-008", "EV-CG-010", "EV-CG-018", "EV-CG-028", "EV-CG-032"]),
            ("falls", "One historical fall and one recent near-fall",
             "Historical fall 8 months prior without fracture; recent incident on 2026-09-06 was caught by caregiver and classified as NEAR_FALL.",
             ["EV-PAT-001", "EV-MR-002", "EV-CG-031"]),
            ("longitudinal_summary", "Evolving Patient Memory Summary",
             "Comprehensive multi-source synthesis preserving independent baseline, real-world caregiver assistance needs, near-fall on 2026-09-06, and recovery on 2026-09-09.",
             ["EV-PAT-002", "EV-DR-001", "EV-DR-005", "EV-CG-006", "EV-CG-011", "EV-CG-018", "EV-CG-031", "EV-CG-036", "EV-CG-040", "EV-CG-041", "EV-LAB-003", "EV-MED-001"])
        ]
        for cat, title, desc, ev_codes in pattern_specs:
            p = db.query(Pattern).filter(Pattern.patient_id == patient.id, Pattern.title == title).first()
            if not p:
                p = Pattern(
                    patient_id=patient.id,
                    category=cat,
                    title=title,
                    description=desc,
                    status=InformationState.AI_DERIVED
                )
                for code in ev_codes:
                    if code in evidence_map:
                        p.supporting_evidences.append(evidence_map[code])
                db.add(p)

        # 9. Conflicts
        conflict_specs = [
            ("mobility", "Independent mobility documentation vs. Caregiver-reported support needs",
             "Doctor documented independent ambulation in clinic on 2026-08-18 (EV-DR-005), whereas caregivers reported unsteadiness and need for support from 2026-08-24 to 2026-09-08 (EV-CG-006 to EV-CG-036).",
             "Patient ambulates independently with steady gait.",
             "Patient needed holding table, arm support, and had near-fall.",
             ConflictStatus.CONFLICTING,
             ["EV-DR-005", "EV-CG-006", "EV-CG-011", "EV-CG-021", "EV-CG-031", "EV-CG-036"]),
            ("falls", "Clinic report of no recent falls vs. Caregiver-reported near-fall",
             "Doctor noted no recent falls on 2026-08-18. Caregiver reported near-fall on 2026-09-06 where patient was caught. Validated as distinct clinical entities (FALL != NEAR_FALL).",
             "No recent falls reported.",
             "Near-fall near bathroom; caught before impact.",
             ConflictStatus.REQUIRES_CLINICIAN_REVIEW,
             ["EV-DR-004", "EV-DR-005", "EV-CG-031"]),
            ("nutrition", "Stable metabolic status vs. Multi-day dietary appetite dip",
             "Doctor/Labs document stable glycemic control (HbA1c 7.4%), while caregivers recorded temporary appetite dip between 08-28 and 09-03 before recovery on 09-05.",
             "Stable nutritional and chronic metabolic control.",
             "Left half of lunch; ate few bites at dinner.",
             ConflictStatus.REQUIRES_CLINICIAN_REVIEW,
             ["EV-DR-005", "EV-LAB-003", "EV-CG-012", "EV-CG-023"])
        ]
        for cat, title, desc, dr_v, cg_v, c_status, ev_codes in conflict_specs:
            c = db.query(Conflict).filter(Conflict.patient_id == patient.id, Conflict.title == title).first()
            if not c:
                c = Conflict(
                    patient_id=patient.id,
                    category=cat,
                    title=title,
                    description=desc,
                    doctor_view=dr_v,
                    caregiver_view=cg_v,
                    status=c_status
                )
                for code in ev_codes:
                    if code in evidence_map:
                        c.supporting_evidences.append(evidence_map[code])
                db.add(c)

        # 10. Memory Pages
        wiki_dir = kb_path / "Patient Wiki" / "P001 Meenakshi Raman"
        for root, dirs, files in os.walk(wiki_dir):
            for file_name in files:
                if file_name.endswith(".md"):
                    p_file = Path(root) / file_name
                    rel_p = os.path.relpath(p_file, kb_path)
                    content = p_file.read_text(encoding="utf-8")
                    title = p_file.stem
                    page_t = PageType.DERIVED if "Derived" in rel_p else (PageType.CLINICAL if "Clinical" in rel_p else (PageType.CAREGIVER if "Caregiver" in rel_p else PageType.PATIENT))
                    
                    existing_mp = db.query(MemoryPage).filter(MemoryPage.path == rel_p).first()
                    if not existing_mp:
                        mp = MemoryPage(
                            patient_id=patient.id,
                            path=rel_p,
                            title=title,
                            content=content,
                            page_type=page_t
                        )
                        db.add(mp)

        db.commit()

        return {
            "patient_code": patient.patient_code,
            "evidence_count": db.query(Evidence).filter(Evidence.patient_id == patient.id).count(),
            "caregiver_observations_count": db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == patient.id).count(),
            "doctor_records_count": db.query(DoctorRecord).filter(DoctorRecord.patient_id == patient.id).count(),
            "medications_count": db.query(Medication).filter(Medication.patient_id == patient.id).count(),
            "labs_count": db.query(LabRecord).filter(LabRecord.patient_id == patient.id).count(),
            "baselines_count": db.query(Baseline).filter(Baseline.patient_id == patient.id).count(),
            "patterns_count": db.query(Pattern).filter(Pattern.patient_id == patient.id).count(),
            "conflicts_count": db.query(Conflict).filter(Conflict.patient_id == patient.id).count(),
            "memory_pages_count": db.query(MemoryPage).filter(MemoryPage.patient_id == patient.id).count()
        }
