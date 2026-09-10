from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.schemas.memory import ClinicalSummaryResponse
from app.services.memory_service import MemoryService

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

