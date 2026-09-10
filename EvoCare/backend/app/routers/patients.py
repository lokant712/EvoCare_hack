from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User, PatientAccess
from app.models.patient import Patient
from app.models.medication import Medication
from app.models.caregiver_observation import CaregiverObservation
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.schemas.patient import PatientResponse, PatientSummaryResponse
from app.schemas.baseline import BaselineResponse
from app.schemas.pattern import PatternResponse
from app.schemas.conflict import ConflictResponse
from app.schemas.medication import MedicationResponse
from app.schemas.caregiver_observation import CaregiverObservationResponse

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.get("", response_model=List[PatientResponse])
def get_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # If user is ADMIN, return all patients
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    if role_str == "ADMIN":
        return db.query(Patient).all()

    # Otherwise return only patients where user has an active grant
    grants = db.query(PatientAccess).filter(
        PatientAccess.user_id == current_user.id,
        PatientAccess.is_active == True
    ).all()
    patient_codes = [g.patient_code for g in grants]

    return db.query(Patient).filter(Patient.patient_code.in_(patient_codes)).all()

@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return patient

@router.get("/{patient_id}/summary", response_model=PatientSummaryResponse)
def get_patient_summary(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    baselines = db.query(Baseline).filter(Baseline.patient_id == patient.id).all()
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

    meds = db.query(Medication).filter(Medication.patient_id == patient.id).all()
    med_resps = [
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

    recent_cgs = db.query(CaregiverObservation).filter(
        CaregiverObservation.patient_id == patient.id
    ).order_by(CaregiverObservation.observed_at.desc()).limit(10).all()

    cg_resps = [
        CaregiverObservationResponse(
            id=c.id,
            patient_id=c.patient_id,
            evidence_id=c.evidence_id,
            evidence_code=c.evidence.evidence_code if c.evidence else "UNKNOWN",
            caregiver_id=c.caregiver_id,
            source_type="CAREGIVER",
            category=c.category,
            observation_text=c.observation_text,
            attributes=c.attributes,
            observed_at=c.observed_at,
            information_state=c.information_state,
            created_at=c.created_at
        )
        for c in recent_cgs
    ]

    patterns = db.query(Pattern).filter(Pattern.patient_id == patient.id).all()
    pat_resps = [
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

    conflicts = db.query(Conflict).filter(Conflict.patient_id == patient.id).all()
    conf_resps = [
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

    diagnoses = [
        "Type 2 Diabetes Mellitus (ICD-10: E11)",
        "Essential Hypertension (ICD-10: I10)",
        "Hyperlipidemia (ICD-10: E78.5)",
        "Bilateral Knee Osteoarthritis (ICD-10: M17.0)"
    ]

    return PatientSummaryResponse(
        patient=PatientResponse.model_validate(patient),
        baseline=baseline_resps,
        current_diagnoses=diagnoses,
        active_medications=med_resps,
        recent_observations=cg_resps,
        recent_patterns=pat_resps,
        recent_conflicts=conf_resps
    )

