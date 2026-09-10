from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.medication import Medication
from app.schemas.medication import MedicationResponse

router = APIRouter(tags=["Medications"])

@router.get("/patients/{patient_id}/medications", response_model=List[MedicationResponse])
def get_medications(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    meds = db.query(Medication).filter(Medication.patient_id == patient.id).all()
    return [
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

