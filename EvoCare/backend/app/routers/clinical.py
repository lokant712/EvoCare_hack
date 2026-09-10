from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_doctor, verify_patient_access
from app.models.security import User
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.schemas.memory import ClinicalSummaryResponse
from app.schemas.doctor_entry import DoctorEntryBatchRequest, DoctorEntryBatchResponse
from app.services.memory_service import MemoryService
from app.services.doctor_entry_service import DoctorEntryService

router = APIRouter(tags=["Clinical"])

@router.get("/patients/{patient_id}/clinical", response_model=ClinicalSummaryResponse)
def get_clinical_summary(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return MemoryService.get_clinical_summary(db, patient.id)


@router.post("/patients/{patient_id}/entries", response_model=DoctorEntryBatchResponse)
def record_doctor_clinical_entries(
    patient_id: str,
    entry_data: DoctorEntryBatchRequest,
    request: Request,
    current_doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    """
    Doctor-only endpoint to record structured diagnoses and medication prescriptions.
    - Saves structured entries to database
    - Generates immutable evidence codes
    - Converts structured table into a clean Markdown clinical note (.md)
    - Records audit log
    """
    patient = verify_patient_access(str(patient_id), current_doctor, db, request)
    ip = request.client.host if request.client else "127.0.0.1"
    return DoctorEntryService.record_clinical_entries(
        db=db,
        patient=patient,
        doctor=current_doctor,
        data=entry_data,
        ip_address=ip
    )


@router.get("/patients/{patient_id}/entries", response_model=Dict[str, Any])
def get_doctor_clinical_entries(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves recorded doctor diagnoses and prescriptions for this patient.
    """
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    
    doctor_records = db.query(DoctorRecord).filter(
        DoctorRecord.patient_id == patient.id
    ).order_by(DoctorRecord.observed_at.desc()).all()

    medications = db.query(Medication).filter(
        Medication.patient_id == patient.id
    ).order_by(Medication.created_at.desc()).all()

    return {
        "patient_code": patient.patient_code,
        "diagnoses": [
            {
                "id": dr.id,
                "doctor_id": dr.doctor_id,
                "record_type": dr.record_type,
                "content": dr.content,
                "observed_at": dr.observed_at.strftime("%Y-%m-%d %H:%M") if dr.observed_at else None,
                "evidence_code": dr.evidence.evidence_code if dr.evidence else "N/A"
            }
            for dr in doctor_records
        ],
        "medications": [
            {
                "id": m.id,
                "name": m.name,
                "dose": m.dose,
                "frequency": m.frequency,
                "status": m.status,
                "indication": m.indication,
                "start_date": m.start_date.strftime("%Y-%m-%d") if m.start_date else None,
                "evidence_code": m.evidence.evidence_code if m.evidence else "N/A"
            }
            for m in medications
        ]
    }

