from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.models.caregiver_observation import CaregiverObservation
from app.schemas.clarification import (
    ObservationStartRequest,
    ObservationStartResponse,
    ClarificationQuestionResponse,
    ClarificationAnswerRequest,
    ClarificationAnswerResponse,
    ClarificationSessionResponse,
    ObservationCompleteResponse,
    StructuredObservationDetailResponse
)
from app.services.observation_pipeline_service import ObservationPipelineService
from app.services.audit_service import AuditService

router = APIRouter(tags=["Caregiver Observation Intelligence & Clarification"])

@router.post("/observations/start", response_model=ObservationStartResponse, status_code=status.HTTP_201_CREATED)
def start_observation_pipeline(
    payload: ObservationStartRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_patient = payload.patient_code or payload.patient_id or "P001"
    patient = verify_patient_access(str(target_patient), current_user, db, request)

    result = ObservationPipelineService.start_session(
        db=db,
        patient_id_or_code=patient.patient_code,
        raw_text=payload.text,
        caregiver_id=payload.caregiver_id or current_user.username or "CG001",
        processing_mode=payload.processing_mode or "AUTO"
    )


    session_id_val = result.get("session_id") if isinstance(result, dict) else getattr(result, "session_id", "N/A")

    AuditService.log_audit_event(
        db=db,
        action="OBSERVATION_SUBMIT",
        user_id=current_user.id,
        username=current_user.username,
        role=current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        patient_id=patient.patient_code,
        resource_type="OBSERVATION_SESSION",
        resource_id=str(session_id_val),
        result="SUCCESS"
    )

    return result



@router.get("/clarification/{session_id}", response_model=ClarificationSessionResponse)
def get_clarification_session(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sess = ObservationPipelineService.get_session(db, session_id)
    verify_patient_access(str(sess.patient_id), current_user, db, request)

    return ClarificationSessionResponse(
        id=sess.id,
        session_code=sess.session_code,
        patient_id=sess.patient_id,
        patient_code=sess.patient.patient_code if sess.patient else "P001",
        raw_text=sess.raw_text,
        detected_category=sess.detected_category,
        status=sess.status,
        questions=[ClarificationQuestionResponse.model_validate(q) for q in sess.questions],
        answers=[ClarificationAnswerResponse.model_validate(a) for a in sess.answers],
        started_at=sess.started_at,
        completed_at=sess.completed_at
    )

@router.post("/clarification/{session_id}/answer", response_model=ClarificationAnswerResponse)
def submit_clarification_answer(
    session_id: int,
    payload: ClarificationAnswerRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sess = ObservationPipelineService.get_session(db, session_id)
    verify_patient_access(str(sess.patient_id), current_user, db, request)

    ans = ObservationPipelineService.answer_question(
        db=db,
        session_id=session_id,
        question_id=payload.question_id,
        field_name=payload.field_name,
        answer_text=payload.answer
    )
    return ans

@router.post("/clarification/{session_id}/complete", response_model=ObservationCompleteResponse)
def complete_clarification_pipeline(
    session_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sess = ObservationPipelineService.get_session(db, session_id)
    verify_patient_access(str(sess.patient_id), current_user, db, request)

    return ObservationPipelineService.complete_session(db, session_id)

@router.get("/observations/{observation_id}", response_model=StructuredObservationDetailResponse)
def get_structured_observation(
    observation_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    obs = db.query(CaregiverObservation).filter(CaregiverObservation.id == observation_id).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caregiver observation with id {observation_id} not found"
        )
    verify_patient_access(str(obs.patient_id), current_user, db, request)

    return StructuredObservationDetailResponse(
        id=obs.id,
        patient_id=obs.patient_id,
        evidence_id=obs.evidence_id,
        evidence_code=obs.evidence.evidence_code if obs.evidence else "UNKNOWN",
        source_type="CAREGIVER",
        category=obs.category,
        observation_text=obs.observation_text,
        attributes=obs.attributes,
        observed_at=obs.observed_at,
        information_state=obs.information_state.value,
        clarification_completed=True
    )

