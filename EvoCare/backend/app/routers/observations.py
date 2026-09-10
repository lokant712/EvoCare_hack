from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.caregiver_observation import CaregiverObservation
from app.schemas.pattern import PatternProvenanceResponse
from app.schemas.conflict import ConflictProvenanceResponse
from app.schemas.evidence import EvidenceResponse
from app.services.provenance_service import ProvenanceService

router = APIRouter(tags=["Provenance & Observations"])

@router.get("/patterns/{pattern_id}/evidence", response_model=PatternProvenanceResponse)
def get_pattern_evidence(
    pattern_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pat = db.query(Pattern).filter(Pattern.id == pattern_id).first()
    if not pat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Pattern {pattern_id} not found")
    verify_patient_access(str(pat.patient_id), current_user, db, request)
    return ProvenanceService.get_pattern_provenance(db, pattern_id)

@router.get("/conflicts/{conflict_id}/evidence", response_model=ConflictProvenanceResponse)
def get_conflict_evidence(
    conflict_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    conf = db.query(Conflict).filter(Conflict.id == conflict_id).first()
    if not conf:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Conflict {conflict_id} not found")
    verify_patient_access(str(conf.patient_id), current_user, db, request)
    return ProvenanceService.get_conflict_provenance(db, conflict_id)

@router.get("/observations/{observation_id}/evidence", response_model=EvidenceResponse)
def get_observation_evidence(
    observation_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obs = db.query(CaregiverObservation).filter(CaregiverObservation.id == observation_id).first()
    if not obs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Observation {observation_id} not found")
    verify_patient_access(str(obs.patient_id), current_user, db, request)
    return ProvenanceService.get_observation_provenance(db, observation_id)

