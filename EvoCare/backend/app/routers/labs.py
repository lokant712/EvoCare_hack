from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.lab import LabRecord
from app.schemas.lab import LabRecordResponse

router = APIRouter(tags=["Labs"])

@router.get("/patients/{patient_id}/labs", response_model=List[LabRecordResponse])
def get_labs(
    patient_id: str,
    request: Request,
    date_from: Optional[datetime] = Query(None, description="Start date filter"),
    date_to: Optional[datetime] = Query(None, description="End date filter"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    query = db.query(LabRecord).filter(LabRecord.patient_id == patient.id)
    if date_from:
        query = query.filter(LabRecord.observed_at >= date_from)
    if date_to:
        query = query.filter(LabRecord.observed_at <= date_to)

    labs = query.order_by(LabRecord.observed_at.asc()).all()
    return [
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

