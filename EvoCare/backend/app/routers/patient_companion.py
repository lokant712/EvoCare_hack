import logging
import uuid
import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.services.audit_service import AuditService
from app.services.clinical_context_service import ClinicalContextService
from app.services.llm.resilient_provider import ResilientLLMProvider

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/patients", tags=["Patient Health Companion"])


class PatientCompanionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)


class PatientCompanionResponse(BaseModel):
    patient_code: str
    patient_name: str
    question: str
    answer: str
    disclaimer: str = (
        "This health companion provides informational context from your personal health records. "
        "It does not establish a diagnosis, prescribe medication, or alter clinical treatment. "
        "Please discuss any health changes or concerns with your attending physician (Dr. Ramesh Varma)."
    )


@router.post("/{patient_id}/companion", response_model=PatientCompanionResponse)
def query_patient_companion(
    patient_id: str,
    req_data: PatientCompanionRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Patient-facing Health Companion Chatbot.
    - Allows patients (and their authorized caregivers/doctors) to query their own health records.
    - Plain-language, empathetic, strictly informational grounded answers.
    - Never mutates data; does not provide unverified medical diagnoses.
    """
    ip = request.client.host if request.client else "unknown"

    # 1. Enforce patient authorization grant
    patient = verify_patient_access(patient_id, current_user, db, request)

    # 2. Extract grounded patient context
    try:
        context = ClinicalContextService.build_patient_context(db, patient.patient_code, req_data.question)
    except Exception as e:
        logger.error(f"Failed to build patient context for companion query: {e}")
        context = {"patient": {"patient_code": patient.patient_code, "name": patient.name}}

    # 3. Generate empathetic patient response
    llm = ResilientLLMProvider()
    answer = llm.generate_patient_response(req_data.question, context)

    # 4. Record audit event
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    AuditService.log_audit_event(
        db=db,
        action="PATIENT_COMPANION_QUERY",
        user_id=current_user.id,
        username=current_user.username,
        role=role_str,
        patient_id=patient.patient_code,
        resource_type="PATIENT_COMPANION",
        resource_id=f"COMP-{uuid.uuid4().hex[:6].upper()}",
        result="SUCCESS",
        details={"question": req_data.question[:100]},
        ip_address=ip
    )

    return PatientCompanionResponse(
        patient_code=patient.patient_code,
        patient_name=patient.name,
        question=req_data.question,
        answer=answer
    )
