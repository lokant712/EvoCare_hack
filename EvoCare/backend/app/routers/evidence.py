from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.evidence import Evidence
from app.models.patient import Patient
from app.models.enums import SourceType
from app.schemas.evidence import EvidenceResponse
from app.services.audit_service import AuditService

router = APIRouter(tags=["Evidence"])

@router.get("/patients/{patient_id}/evidence", response_model=List[EvidenceResponse])
def get_patient_evidence(
    patient_id: str,
    request: Request,
    source_type: Optional[SourceType] = Query(None, description="Filter by source type"),
    category: Optional[str] = Query(None, description="Filter by observation category"),
    date_from: Optional[datetime] = Query(None, description="Start observation date"),
    date_to: Optional[datetime] = Query(None, description="End observation date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    query = db.query(Evidence).filter(Evidence.patient_id == patient.id)

    if source_type:
        query = query.filter(Evidence.source_type == source_type)
    if date_from:
        query = query.filter(Evidence.observed_at >= date_from)
    if date_to:
        query = query.filter(Evidence.observed_at <= date_to)

    evidences = query.order_by(Evidence.observed_at.asc()).all()

    if category:
        filtered = []
        for ev in evidences:
            matches = any(c.category.lower() == category.lower() for c in ev.caregiver_observations) or \
                      any(o.category.lower() == category.lower() for o in ev.observations)
            if matches:
                filtered.append(ev)
        return filtered

    return evidences

@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
def get_evidence_by_id(
    evidence_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Look up by ID or by evidence_code (e.g. EV-CG-001)
    if evidence_id.isdigit():
        ev = db.query(Evidence).filter(Evidence.id == int(evidence_id)).first()
    else:
        ev = db.query(Evidence).filter(Evidence.evidence_code == evidence_id).first()

    if not ev:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Evidence with identifier '{evidence_id}' not found"
        )

    # Verify user has access to this evidence's patient
    verify_patient_access(str(ev.patient_id), current_user, db, request)

    return ev

