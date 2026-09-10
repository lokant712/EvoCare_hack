from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, require_doctor, verify_patient_access
from app.models.security import User
from app.models.patient import Patient
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.schemas.baseline import BaselineResponse
from app.schemas.pattern import PatternResponse
from app.schemas.conflict import ConflictResponse
from app.schemas.memory import MemoryResponse
from app.services.memory_service import MemoryService
from app.services.audit_service import AuditService

router = APIRouter(tags=["Memory"])

@router.get("/patients/{patient_id}/baseline", response_model=List[BaselineResponse])
def get_baseline(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    baselines = db.query(Baseline).filter(Baseline.patient_id == patient.id).all()
    return [
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

@router.get("/patients/{patient_id}/patterns", response_model=List[PatternResponse])
def get_patterns(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    patterns = db.query(Pattern).filter(Pattern.patient_id == patient.id).all()
    return [
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

@router.get("/patients/{patient_id}/conflicts", response_model=List[ConflictResponse])
def get_conflicts(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)

    conflicts = db.query(Conflict).filter(Conflict.patient_id == patient.id).all()
    return [
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

@router.get("/patients/{patient_id}/memory", response_model=MemoryResponse)
def get_memory(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return MemoryService.get_longitudinal_memory(db, patient.id)

# -------------------------------------------------------------
# Phase 5 Evolving Patient Memory & Living Patient Wiki Routes
# -------------------------------------------------------------
from app.services.memory import (
    MemoryService as EvolvingMemoryService,
    MemoryConsolidateRequest,
    MemoryProposalResponse,
    MemoryApplyResponse,
    MemoryDiffResponse
)

@router.post("/memory/consolidate", response_model=MemoryProposalResponse, status_code=status.HTTP_201_CREATED)
def consolidate_memory(
    payload: MemoryConsolidateRequest,
    request: Request,
    current_doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    target_patient = payload.patient_id or "P001"
    patient = verify_patient_access(str(target_patient), current_doctor, db, request)

    target_evidence = payload.evidence_id or payload.evidence_code
    if not target_evidence:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Must provide evidence_id or evidence_code")
    
    return EvolvingMemoryService.consolidate_evidence(
        db=db,
        patient_id_or_code=patient.patient_code,
        evidence_id_or_code=target_evidence
    )

@router.post("/memory/apply/{proposal_id}", response_model=MemoryApplyResponse)
def apply_memory_proposal(
    proposal_id: int,
    request: Request,
    current_doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
):
    from app.models.memory_models import MemoryProposal
    prop = db.query(MemoryProposal).filter(MemoryProposal.id == proposal_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal {proposal_id} not found")
    
    # Verify doctor has access to patient
    verify_patient_access(str(prop.patient_id), current_doctor, db, request)

    return EvolvingMemoryService.apply_proposal(db=db, proposal_id=proposal_id)

@router.get("/memory/proposals/{proposal_id}", response_model=MemoryProposalResponse)
def get_memory_proposal_by_id(
    proposal_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from app.models.memory_models import MemoryProposal
    prop = db.query(MemoryProposal).filter(MemoryProposal.id == proposal_id).first()
    if not prop:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal {proposal_id} not found")
    
    patient = verify_patient_access(str(prop.patient_id), current_user, db, request)

    return MemoryProposalResponse(
        proposal_id=prop.id,
        proposal_code=prop.proposal_code,
        patient_id=prop.patient_id,
        patient_code=patient.patient_code if patient else "P001",
        memory_page=prop.memory_page,
        category=prop.category,
        update_type=prop.update_type,
        proposed_claim=prop.proposed_claim,
        information_state=prop.information_state,
        evidence_ids=prop.evidence_ids or [],
        confidence=prop.confidence,
        status=prop.status,
        validation_errors=prop.validation_errors or [],
        created_at=prop.created_at
    )

@router.get("/memory/{patient_id}/summary")
def get_patient_memory_summary(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return EvolvingMemoryService.get_patient_memory_summary(db=db, patient_id=patient.id)

@router.get("/memory/{patient_id}/{page}/history")
def get_page_memory_history(
    patient_id: str,
    page: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return EvolvingMemoryService.get_memory_history(db=db, patient_id=patient.id, page=page)

@router.get("/memory/{patient_id}/{page}/diff", response_model=MemoryDiffResponse)
def get_page_memory_diff(
    patient_id: str,
    page: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return EvolvingMemoryService.get_memory_diff(db=db, patient_id=patient.id, page=page)

@router.get("/memory/{patient_id}/{page}")
def get_current_page_memory(
    patient_id: str,
    page: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient = verify_patient_access(str(patient_id), current_user, db, request)
    return EvolvingMemoryService.get_current_memory(db=db, patient_id=patient.id, page=page)



