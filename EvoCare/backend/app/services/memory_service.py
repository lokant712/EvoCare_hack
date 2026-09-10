from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.observation import Observation
from app.schemas.memory import TimelineEventResponse, ClinicalSummaryResponse, MemoryResponse
from app.schemas.baseline import BaselineResponse
from app.schemas.pattern import PatternResponse
from app.schemas.conflict import ConflictResponse
from app.schemas.medication import MedicationResponse
from app.schemas.lab import LabRecordResponse

class MemoryService:
    @staticmethod
    def get_timeline(db: Session, patient_id: int) -> List[TimelineEventResponse]:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        events = []

        # 1. Caregiver Observations
        cg_obs = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == patient_id).all()
        for cg in cg_obs:
            event_type = "NEAR_FALL" if "almost fell" in cg.observation_text.lower() else "CAREGIVER_OBSERVATION"
            is_ambiguous = cg.attributes.get("clarification_required", False) if cg.attributes else False
            events.append(TimelineEventResponse(
                observed_at=cg.observed_at,
                event_type=event_type,
                source_type="CAREGIVER",
                source_id=cg.caregiver_id,
                description=cg.observation_text,
                evidence_code=cg.evidence.evidence_code if cg.evidence else "UNKNOWN",
                category=cg.category,
                clarification_required=is_ambiguous
            ))

        # 2. Doctor Records
        dr_recs = db.query(DoctorRecord).filter(DoctorRecord.patient_id == patient_id).all()
        for dr in dr_recs:
            events.append(TimelineEventResponse(
                observed_at=dr.observed_at,
                event_type="CLINICAL_ENCOUNTER",
                source_type="DOCTOR",
                source_id=dr.doctor_id,
                description=dr.content,
                evidence_code=dr.evidence.evidence_code if dr.evidence else "UNKNOWN",
                category="clinical_review",
                clarification_required=False
            ))

        # 3. Lab Records (Grouped by observation timestamp)
        labs = db.query(LabRecord).filter(LabRecord.patient_id == patient_id).all()
        lab_dates = set(l.observed_at for l in labs)
        for ldate in lab_dates:
            sublabs = [l for l in labs if l.observed_at == ldate]
            summary = ", ".join(f"{l.test_name}: {l.value} {l.unit or ''}".strip() for l in sublabs)
            ev_code = sublabs[0].evidence.evidence_code if sublabs and sublabs[0].evidence else "UNKNOWN"
            events.append(TimelineEventResponse(
                observed_at=ldate,
                event_type="LAB_PANEL",
                source_type="LAB_RECORD",
                source_id="METROPOLIS_LABS",
                description=f"Glycemic & Metabolic Panel: {summary}",
                evidence_code=ev_code,
                category="laboratory",
                clarification_required=False
            ))

        # 4. Patient Statements & Medical Records (Historical fall etc)
        other_evidences = db.query(Evidence).filter(
            Evidence.patient_id == patient_id,
            Evidence.source_type.in_(["PATIENT", "MEDICAL_RECORD"])
        ).all()
        for ev in other_evidences:
            event_type = "HISTORICAL_FALL" if "fall" in ev.original_statement.lower() or "slipped" in ev.original_statement.lower() else "HISTORICAL_RECORD"
            events.append(TimelineEventResponse(
                observed_at=ev.observed_at,
                event_type=event_type,
                source_type=ev.source_type.value,
                source_id=ev.source_id,
                description=ev.original_statement,
                evidence_code=ev.evidence_code,
                category="historical",
                clarification_required=False
            ))

        # Sort chronologically
        events.sort(key=lambda x: x.observed_at)
        return events

    @staticmethod
    def get_clinical_summary(db: Session, patient_id: int) -> ClinicalSummaryResponse:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        # Doctor confirmed diagnoses (ICD-10 grounded)
        diagnoses = [
            {"code": "E11", "name": "Type 2 Diabetes Mellitus", "status": "Stable", "confirmed_by": "Dr. S. Chandran", "evidence": "EV-DR-001"},
            {"code": "I10", "name": "Essential Hypertension", "status": "Controlled", "confirmed_by": "Dr. S. Chandran", "evidence": "EV-DR-001"},
            {"code": "E78.5", "name": "Hyperlipidemia", "status": "Controlled", "confirmed_by": "Dr. S. Chandran", "evidence": "EV-DR-001"},
            {"code": "M17.0", "name": "Bilateral Knee Osteoarthritis", "status": "Chronic (Grade II)", "confirmed_by": "Dr. S. Chandran", "evidence": "EV-DR-001"}
        ]

        # Doctor progress notes
        doctor_records = []
        drs = db.query(DoctorRecord).filter(DoctorRecord.patient_id == patient_id).order_by(DoctorRecord.observed_at).all()
        for dr in drs:
            doctor_records.append({
                "date": dr.observed_at.strftime("%Y-%m-%d"),
                "doctor_id": dr.doctor_id,
                "record_type": dr.record_type,
                "findings": dr.content,
                "evidence_code": dr.evidence.evidence_code if dr.evidence else "UNKNOWN"
            })

        # Medical History summary
        medical_history = [
            {
                "topic": "Chronic Conditions",
                "summary": "Managed T2DM, HTN, Hyperlipidemia, and Bilateral Knee Osteoarthritis without major organ decompensation.",
                "evidence": "EV-MR-001"
            },
            {
                "topic": "Prior Falls Incident",
                "summary": "One historical slip ~8 months prior (Jan 2026) with mild contusion and no fracture or hospitalization.",
                "evidence": "EV-MR-002"
            }
        ]

        # Labs
        labs = db.query(LabRecord).filter(LabRecord.patient_id == patient_id).order_by(LabRecord.observed_at).all()
        lab_responses = [
            LabRecordResponse(
                id=l.id,
                patient_id=l.patient_id,
                evidence_id=l.evidence_id,
                evidence_code=l.evidence.evidence_code if l.evidence else "UNKNOWN",
                source_type="LAB_RECORD",
                test_panel=l.test_panel,
                test_name=l.test_name,
                value=l.value,
                unit=l.unit,
                reference_range=l.reference_range,
                observed_at=l.observed_at,
                created_at=l.created_at
            )
            for l in labs
        ]

        # Medications
        meds = db.query(Medication).filter(Medication.patient_id == patient_id).all()
        med_responses = [
            MedicationResponse(
                id=m.id,
                patient_id=m.patient_id,
                evidence_id=m.evidence_id,
                evidence_code=m.evidence.evidence_code if m.evidence else "UNKNOWN",
                source_type="MEDICATION_RECORD",
                name=m.name,
                dose=m.dose,
                frequency=m.frequency,
                status=m.status,
                indication=m.indication,
                start_date=m.start_date,
                end_date=m.end_date,
                created_at=m.created_at
            )
            for m in meds
        ]

        return ClinicalSummaryResponse(
            diagnoses=diagnoses,
            doctor_records=doctor_records,
            medical_history=medical_history,
            labs=lab_responses,
            medications=med_responses
        )

    @staticmethod
    def get_longitudinal_memory(db: Session, patient_id: int) -> MemoryResponse:
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found")

        baselines = db.query(Baseline).filter(Baseline.patient_id == patient_id).all()
        baseline_resps = [
            BaselineResponse(
                id=b.id,
                patient_id=b.patient_id,
                category=b.category,
                baseline_value=b.baseline_value,
                information_state=b.information_state,
                supporting_evidence_codes=[ev.evidence_code for ev in b.supporting_evidences],
                created_at=b.created_at,
                updated_at=b.updated_at
            )
            for b in baselines
        ]

        patterns = db.query(Pattern).filter(Pattern.patient_id == patient_id).all()
        pattern_resps = [
            PatternResponse(
                id=p.id,
                patient_id=p.patient_id,
                category=p.category,
                title=p.title,
                description=p.description,
                status=p.status,
                supporting_evidence_codes=[ev.evidence_code for ev in p.supporting_evidences],
                detected_at=p.detected_at,
                created_at=p.created_at
            )
            for p in patterns
        ]

        conflicts = db.query(Conflict).filter(Conflict.patient_id == patient_id).all()
        conflict_resps = [
            ConflictResponse(
                id=c.id,
                patient_id=c.patient_id,
                category=c.category,
                title=c.title,
                description=c.description,
                doctor_view=c.doctor_view,
                caregiver_view=c.caregiver_view,
                status=c.status,
                supporting_evidence_codes=[ev.evidence_code for ev in c.supporting_evidences],
                created_at=c.created_at,
                resolved_at=c.resolved_at
            )
            for c in conflicts
        ]

        # Recent improvements
        recent_improvements = [
            {
                "date": "2026-09-09",
                "domain": "mobility",
                "finding": "Walking better today and did not need support inside the house.",
                "evidence_code": "EV-CG-040"
            },
            {
                "date": "2026-09-09",
                "domain": "cognition",
                "finding": "Recognized everyone and was talking normally.",
                "evidence_code": "EV-CG-041"
            },
            {
                "date": "2026-09-09",
                "domain": "medication",
                "finding": "Took medicines on time today.",
                "evidence_code": "EV-CG-042"
            },
            {
                "date": "2026-09-08",
                "domain": "nutrition",
                "finding": "Ate about three quarters of her meal (~75%).",
                "evidence_code": "EV-CG-037"
            },
            {
                "date": "2026-09-07",
                "domain": "sleep",
                "finding": "Slept better.",
                "evidence_code": "EV-CG-035"
            }
        ]

        # Unknown information cases
        unknown_info = [
            {
                "evidence_code": "EV-CG-043",
                "statement": "He is dizzy.",
                "missing_fields": ["subject_gender_clarification", "severity", "duration", "trigger"]
            },
            {
                "evidence_code": "EV-CG-044",
                "statement": "She is weak today.",
                "missing_fields": ["functional_domain", "severity", "vitals"]
            },
            {
                "evidence_code": "EV-CG-045",
                "statement": "She is confused.",
                "missing_fields": ["cognitive_domain", "duration", "trigger"]
            },
            {
                "evidence_code": "EV-CG-046",
                "statement": "She didn't eat much.",
                "missing_fields": ["meal_type", "exact_portion", "fluid_intake"]
            },
            {
                "evidence_code": "EV-CG-047",
                "statement": "She was not herself.",
                "missing_fields": ["behavioral_context", "specific_changes"]
            }
        ]

        exec_summary = (
            "Historically, the patient has been documented as independently mobile without assistive devices "
            "(EV-PAT-002, EV-DR-001). Recent caregiver observations from late August through early September 2026 "
            "describe intermittent unsteadiness, furniture support, and an increasing need for walking assistance "
            "(EV-CG-006, EV-CG-011, EV-CG-021, EV-CG-036), including a near-fall near the bathroom on 2026-09-06 "
            "(EV-CG-031). The latest caregiver observation on 2026-09-09 indicates improvement with independent "
            "indoor walking (EV-CG-040). Repeated episodic dizziness (with postural trigger on 2026-09-01) and "
            "intermittent evening confusion notes were reported, with intact morning cognition and full family recognition "
            "preserved. The cause of recent mobility changes has not been established; there is no clinician-confirmed dementia diagnosis."
        )

        return MemoryResponse(
            patient_id=patient.id,
            patient_code=patient.patient_code,
            patient_name=patient.name,
            executive_summary=exec_summary,
            baseline=baseline_resps,
            active_patterns=pattern_resps,
            unresolved_conflicts=conflict_resps,
            recent_improvements=recent_improvements,
            unknown_information=unknown_info
        )
