from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.patient import Patient
from app.models.caregiver_observation import CaregiverObservation
from app.schemas.caregiver_observation import CaregiverObservationResponse

router = APIRouter(tags=["Caregiver Observations"])

@router.get("/patients/{patient_id}/caregiver-observations", response_model=List[CaregiverObservationResponse])
def get_caregiver_observations(
    patient_id: str,
    request: Request,
    category: Optional[str] = Query(None, description="Filter by category (e.g., mobility, dizziness, cognition)"),
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    query = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == patient.id)

    if category:
        query = query.filter(CaregiverObservation.category.ilike(f"%{category}%"))
    if date_from:
        query = query.filter(CaregiverObservation.observed_at >= date_from)
    if date_to:
        query = query.filter(CaregiverObservation.observed_at <= date_to)

    observations = query.order_by(CaregiverObservation.observed_at.asc()).all()

    return [
        CaregiverObservationResponse(
            id=o.id,
            patient_id=o.patient_id,
            evidence_id=o.evidence_id,
            evidence_code=o.evidence.evidence_code if o.evidence else "UNKNOWN",
            caregiver_id=o.caregiver_id,
            source_type="CAREGIVER",
            category=o.category,
            observation_text=o.observation_text,
            attributes=o.attributes,
            observed_at=o.observed_at,
            information_state=o.information_state,
            created_at=o.created_at
        )
        for o in observations
    ]

