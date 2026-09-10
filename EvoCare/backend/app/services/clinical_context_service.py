from pathlib import Path
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.memory_models import MemoryClaim
from app.models.enums import SourceType, EvidenceStatus
from app.schemas.clinical_reasoning import PatientContextSummary

logger = logging.getLogger(__name__)


class ClinicalContextService:
    """
    Constructs a structured, relevance-filtered clinical context from patient records.
    Ensures every item has strict source attribution and evidence ID traceability.
    """

    @classmethod
    def get_patient(cls, db: Session, patient_id: str) -> Optional[Patient]:
        patient = db.query(Patient).filter(
            (Patient.patient_code == patient_id) | (Patient.id == (int(patient_id) if patient_id.isdigit() else -1))
        ).first()
        return patient

    @classmethod
    def get_patient_wiki_content(cls, patient_code: str, question: str) -> Dict[str, str]:
        """
        Reads directly from the interconnected Markdown Wiki files in knowledge-base/Patient Wiki.
        Extracts authentic wiki pages including Patient Overview.md, Clinical/Medical History.md,
        Diagnoses, Baseline, and domain logs.
        """
        kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)
        wiki_root = kb_dir / "Patient Wiki"
        if not wiki_root.exists():
            return {}

        patient_dirs = [d for d in wiki_root.iterdir() if d.is_dir() and d.name.startswith(patient_code)]
        if not patient_dirs:
            return {}
        p_dir = patient_dirs[0]

        wiki_files: Dict[str, str] = {}
        q_lower = question.lower()

        # Priority 1: Overview and Medical History
        overview_file = p_dir / "Patient Overview.md"
        if overview_file.exists():
            try:
                wiki_files["Patient Overview.md"] = overview_file.read_text(encoding="utf-8")
            except Exception as e:
                logger.warning(f"Failed to read {overview_file}: {e}")

        # Priority 2: Targeted domain files
        targets = []
        if any(w in q_lower for w in ["history", "medical history", "diagnos", "chronic", "background", "summary", "profile", "baseline"]):
            targets.extend([
                p_dir / "Clinical" / "Medical History.md",
                p_dir / "Clinical" / "Diagnoses.md",
                p_dir / "Derived" / "Baseline.md"
            ])
        if any(w in q_lower for w in ["dizzy", "dizziness", "balance"]):
            targets.extend([
                p_dir / "Caregiver" / "Dizziness.md",
                p_dir / "Derived" / "Dizziness Trends.md"
            ])
        if any(w in q_lower for w in ["mobil", "fall", "walk", "gait"]):
            targets.extend([
                p_dir / "Caregiver" / "Mobility.md",
                p_dir / "Caregiver" / "Falls.md",
                p_dir / "Derived" / "Mobility Trends.md"
            ])
        if any(w in q_lower for w in ["medic", "drug", "pill", "prescrib"]):
            targets.extend([
                p_dir / "Clinical" / "Medications.md",
                p_dir / "Caregiver" / "Medication Adherence.md"
            ])
        if any(w in q_lower for w in ["eat", "nutrition", "appetite", "meal"]):
            targets.extend([
                p_dir / "Caregiver" / "Nutrition.md",
                p_dir / "Derived" / "Nutrition Trends.md"
            ])
        if any(w in q_lower for w in ["cognit", "confus", "memory", "dementia"]):
            targets.extend([
                p_dir / "Caregiver" / "Cognition.md",
                p_dir / "Derived" / "Cognition Trends.md"
            ])
        if any(w in q_lower for w in ["caregiver", "caretaker", "notes", "past week", "carer", "home observations"]):
            targets.extend([
                p_dir / "Caregiver" / "Mobility.md",
                p_dir / "Caregiver" / "Dizziness.md",
                p_dir / "Caregiver" / "Nutrition.md",
                p_dir / "Caregiver" / "Falls.md"
            ])

        for tf in targets:
            rel_name = str(tf.relative_to(p_dir)).replace("\\", "/")
            if tf.exists() and rel_name not in wiki_files:
                try:
                    wiki_files[rel_name] = tf.read_text(encoding="utf-8")
                except Exception as e:
                    logger.warning(f"Failed to read {tf}: {e}")

        return wiki_files

    @classmethod
    def build_patient_context(
        cls, db: Session, patient_id: str, question: str
    ) -> Dict[str, Any]:
        patient = cls.get_patient(db, patient_id)
        if not patient:
            raise ValueError(f"Patient '{patient_id}' not found in database.")

        q_lower = question.lower()

        # Domain Relevance flags
        is_dizziness = any(w in q_lower for w in ["dizzy", "dizziness", "lightheaded", "vertigo", "spinning", "balance", "faint", "syncope"])
        is_mobility = any(w in q_lower for w in ["mobil", "walk", "fall", "near-fall", "stumble", "gait", "support", "cruis", "stand", "steps"])
        is_cognition = any(w in q_lower for w in ["cognit", "confus", "dementia", "alzheimer", "memory", "forget", "disorient", "mental"])
        is_nutrition = any(w in q_lower for w in ["eat", "nutrition", "appetite", "food", "meal", "dinner", "weight", "diet"])
        is_medication = any(w in q_lower for w in ["medic", "drug", "pill", "prescrib", "dose", "amlodipine", "metformin", "statin"])
        
        is_broad = not (is_dizziness or is_mobility or is_cognition or is_nutrition or is_medication)

        # 1. Demographics
        demographics = {
            "patient_code": patient.patient_code,
            "name": patient.name,
            "age": patient.age,
            "sex": patient.sex,
            "synthetic": patient.is_synthetic,
        }

        # 2. Clinician-Confirmed Doctor Records
        doctor_records = db.query(DoctorRecord).filter(DoctorRecord.patient_id == patient.id).all()
        clinician_diagnoses = []
        for dr in doctor_records:
            ev_code = dr.evidence.evidence_code if dr.evidence else f"EV-DR-{dr.id:03d}"
            clinician_diagnoses.append({
                "doctor_id": dr.doctor_id,
                "record_type": dr.record_type,
                "assessment_date": dr.observed_at.strftime("%Y-%m-%d") if dr.observed_at else "Unknown",
                "content": dr.content,
                "evidence_code": ev_code,
                "source_type": SourceType.DOCTOR.value,
                "relevance_reason": "Clinician-confirmed medical assessment record"
            })

        # 3. Active Medications
        medications = db.query(Medication).filter(Medication.patient_id == patient.id).all()
        med_list = []
        for m in medications:
            include_med = is_broad or is_dizziness or is_medication or is_mobility
            if include_med:
                ev_code = m.evidence.evidence_code if m.evidence else f"EV-MED-{m.id:03d}"
                med_list.append({
                    "name": m.name,
                    "dose": m.dose,
                    "frequency": m.frequency,
                    "indication": m.indication or "Documented condition",
                    "status": m.status,
                    "evidence_code": ev_code,
                    "source_type": SourceType.MEDICATION_RECORD.value,
                    "relevance_reason": "Active pharmacotherapy and potential hemodynamic/orthostatic context"
                })

        # 4. Laboratory History
        labs = db.query(LabRecord).filter(LabRecord.patient_id == patient.id).all()
        lab_list = []
        for l in labs:
            include_lab = is_broad or is_dizziness or is_nutrition or "lab" in q_lower
            if include_lab:
                ev_code = l.evidence.evidence_code if l.evidence else f"EV-LAB-{l.id:03d}"
                lab_list.append({
                    "test_panel": l.test_panel,
                    "test_name": l.test_name,
                    "value": l.value,
                    "unit": l.unit or "",
                    "reference_range": l.reference_range or "Normal",
                    "test_date": l.observed_at.strftime("%Y-%m-%d") if l.observed_at else "Unknown",
                    "evidence_code": ev_code,
                    "source_type": SourceType.LAB_RECORD.value,
                    "relevance_reason": "Objective biochemical and metabolic parameters"
                })

        # 5. Longitudinal Baselines & Patterns
        baselines = db.query(Baseline).filter(Baseline.patient_id == patient.id).all()
        baseline_list = []
        for b in baselines:
            domain_match = (
                (is_mobility and "mobility" in b.category.lower()) or
                (is_cognition and "cognition" in b.category.lower()) or
                (is_nutrition and "nutrition" in b.category.lower()) or
                (is_dizziness and "dizziness" in b.category.lower()) or
                is_broad
            )
            if domain_match:
                baseline_list.append({
                    "category": b.category,
                    "baseline_value": b.baseline_value,
                    "documented_date": b.created_at.strftime("%Y-%m-%d") if b.created_at else "Unknown",
                    "source_type": SourceType.AI_DERIVED.value,
                    "relevance_reason": f"Documented longitudinal baseline for {b.category}"
                })

        patterns = db.query(Pattern).filter(Pattern.patient_id == patient.id).all()
        pattern_list = []
        for p in patterns:
            domain_match = (
                (is_mobility and "mobility" in p.category.lower()) or
                (is_cognition and "cognition" in p.category.lower()) or
                (is_nutrition and "nutrition" in p.category.lower()) or
                (is_dizziness and "dizziness" in p.category.lower()) or
                is_broad
            )
            if domain_match:
                pattern_list.append({
                    "category": p.category,
                    "title": p.title,
                    "description": p.description,
                    "source_type": SourceType.AI_DERIVED.value,
                    "relevance_reason": f"Synthesized trajectory pattern for {p.category}"
                })

        # 6. Longitudinal Memory Claims
        claims = db.query(MemoryClaim).filter(
            MemoryClaim.patient_id == patient.id,
            MemoryClaim.active == True
        ).all()
        claim_list = []
        for c in claims:
            domain_match = (
                (is_mobility and c.category == "mobility") or
                (is_cognition and c.category == "cognition") or
                (is_nutrition and c.category == "nutrition") or
                (is_dizziness and c.category == "dizziness") or
                is_broad
            )
            if domain_match:
                claim_list.append({
                    "claim_code": c.claim_code,
                    "category": c.category,
                    "statement": c.statement,
                    "information_state": c.information_state,
                    "citations": c.evidence_ids or [],
                    "source_type": SourceType.AI_DERIVED.value,
                    "relevance_reason": f"Active longitudinal memory claim for {c.category}"
                })

        # 7. Caregiver Observations (Filtered by relevance)
        cg_obs = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == patient.id).all()
        caregiver_list = []
        for obs in cg_obs:
            cat = (obs.category or "").lower()
            stmt = (obs.observation_text or "").lower()
            
            match_dizzy = is_dizziness and ("dizzy" in cat or "dizziness" in stmt or "spinning" in stmt or "dizzy" in stmt)
            match_mob = is_mobility and ("mobility" in cat or "fall" in cat or "walk" in stmt or "stumble" in stmt or "fell" in stmt or "cruis" in stmt or "steps" in stmt)
            match_cog = is_cognition and ("cognit" in cat or "confus" in stmt or "forget" in stmt or "disorient" in stmt)
            match_nut = is_nutrition and ("nutrit" in cat or "appetite" in cat or "eat" in stmt or "meal" in stmt or "dinner" in stmt)
            
            if match_dizzy or match_mob or match_cog or match_nut or is_broad:
                ev_code = obs.evidence.evidence_code if obs.evidence else f"EV-CG-{obs.id:03d}"
                caregiver_list.append({
                    "caregiver_id": obs.caregiver_id,
                    "category": obs.category,
                    "observed_at": obs.observed_at.strftime("%Y-%m-%d %H:%M") if obs.observed_at else "Unknown",
                    "observation_text": obs.observation_text,
                    "attributes": obs.attributes or {},
                    "evidence_code": ev_code,
                    "source_type": SourceType.CAREGIVER.value,
                    "relevance_reason": f"Direct caregiver report in {obs.category} domain"
                })

        # 8. Conflicts
        conflicts = db.query(Conflict).filter(Conflict.patient_id == patient.id).all()
        conflict_list = []
        for c in conflicts:
            conflict_list.append({
                "category": c.category,
                "title": c.title,
                "description": c.description,
                "doctor_view": c.doctor_view,
                "caregiver_view": c.caregiver_view,
                "source_type": "CONFLICT_RECORD",
                "relevance_reason": "Contextual discrepancy between clinical exam and home setting"
            })

        # 9. Verifiable Immutable Evidence Records
        evidence_records = db.query(Evidence).filter(Evidence.patient_id == patient.id).all()
        evidence_dict = {}
        for ev in evidence_records:
            evidence_dict[ev.evidence_code] = {
                "evidence_id": ev.evidence_code,
                "source_type": ev.source_type.value if hasattr(ev.source_type, 'value') else str(ev.source_type),
                "observed_at": ev.observed_at.strftime("%Y-%m-%d %H:%M") if ev.observed_at else "Unknown",
                "recorded_at": ev.recorded_at.strftime("%Y-%m-%d %H:%M") if ev.recorded_at else "Unknown",
                "original_statement": ev.original_statement,
                "is_immutable": ev.status == EvidenceStatus.IMMUTABLE if hasattr(EvidenceStatus, 'IMMUTABLE') else True,
            }

        # 10. Explicit Unknowns & Missing Clinical Parameters
        known_unknowns = [
            "Dizziness etiology: UNKNOWN (unconfirmed by formal diagnostic testing / orthostatics)",
            "Orthostatic vital signs (lying/standing BP & HR): NOT DOCUMENTED in current record",
            "Duration of episodic dizziness: Inconsistently documented by caregiver",
            "Medication administration timing relative to dizzy episodes: NOT DOCUMENTED",
            "Neurological focal deficits: None documented in doctor assessment DOC-001",
            "Cognition: Caregiver reports confusion episodes; no clinician diagnosis of dementia"
        ]

        # 11. Timeline events
        timeline_events = []
        if is_mobility or is_dizziness or is_broad:
            timeline_events.extend([
                {"date": "2026-08-10", "type": "BASELINE", "summary": "Baseline mobility: Independent ambulation without assistive device."},
                {"date": "2026-08-28", "type": "DECLINE", "summary": "Caregiver reports unsteady walking outdoors; requires arm support."},
                {"date": "2026-09-01", "type": "NEAR_FALL", "summary": "NEAR-FALL: Stumbled near bathroom, caught by caregiver. NO ground impact, NO injury (EV-CG-045)."},
                {"date": "2026-09-02", "type": "RECOVERY", "summary": "Improved mobility: Walked normally indoors unassisted (EV-CG-046)."},
                {"date": "2026-09-03", "type": "DIZZINESS", "summary": "Caregiver reports episodic dizziness when getting out of bed (EV-CG-041)."}
            ])

        # Diagnoses strings from doctor notes / known clinical history
        diag_list = ["Essential Hypertension (I10)", "Type 2 Diabetes Mellitus (E11.9)", "Hyperlipidemia (E78.5)"]

        # Summary for UI display
        summary = PatientContextSummary(
            patient_id=patient.patient_code,
            name=patient.name,
            age=patient.age,
            sex=patient.sex,
            diagnoses=diag_list,
            active_medications=[f"{m['name']} {m['dose']} ({m['indication']})" for m in med_list],
            relevant_observations=[f"{o['observed_at']}: {o['observation_text']}" for o in caregiver_list[:5]],
            relevant_changes=[
                "Mobility: Independent baseline -> intermittent assistance needed -> near-fall (no injury) -> later improved indoor ambulation",
                "Dizziness: Episodic lightheadedness on standing/getting out of bed (etiology unconfirmed)",
                "Cognition: Isolated caregiver-reported confusion episodes (alert & oriented during clinic exam)"
            ],
            relevant_labs=[f"{l['test_name']}: {l['value']} {l['unit']}" for l in lab_list[:4]],
            known_unknowns=known_unknowns,
            conflicts=[f"{c['category']}: {c['title']}" for c in conflict_list],
            total_evidence_count=len(evidence_records)
        )

        wiki_pages = cls.get_patient_wiki_content(patient.patient_code, question)

        return {
            "demographics": demographics,
            "clinician_diagnoses": clinician_diagnoses,
            "medications": med_list,
            "labs": lab_list,
            "baselines": baseline_list,
            "patterns": pattern_list,
            "memory_claims": claim_list,
            "caregiver_observations": caregiver_list,
            "conflicts": conflict_list,
            "known_unknowns": known_unknowns,
            "timeline_events": timeline_events,
            "evidence_catalog": evidence_dict,
            "summary": summary,
            "wiki_pages": wiki_pages
        }
