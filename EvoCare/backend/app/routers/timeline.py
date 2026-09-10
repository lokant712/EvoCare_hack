from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.schemas.memory import TimelineEventResponse
from app.services.memory_service import MemoryService

router = APIRouter(tags=["Timeline"])

@router.get("/patients/{patient_id}/timeline", response_model=List[TimelineEventResponse])
def get_patient_timeline(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return MemoryService.get_timeline(db, patient.id)

