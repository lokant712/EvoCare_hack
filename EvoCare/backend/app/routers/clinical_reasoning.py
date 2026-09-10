import uuid
import re
import logging
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import require_doctor, verify_patient_access
from app.models.security import User
from app.models.reasoning_session import ReasoningSession
from app.schemas.clinical_reasoning import (
    ClinicalReasoningRequest,
    ClinicalReasoningResponse,
    ClinicalConsideration,
)
from app.services.clinical_context_service import ClinicalContextService
from app.services.clinical_reasoning_validator import ClinicalReasoningValidator
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/clinical-reasoning",
    tags=["Doctor-Only Clinical Reasoning Assistant"]
)

# Known prompt injection signatures
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|rules|guidelines)",
    r"system\s*prompt\s*override",
    r"act\s+as\s+(an\s+)?unrestricted",
    r"bypass\s+(safety|security|clinical\s+rules)",
    r"diagnose\s+directly\s+and\s+ignore\s+rules",
    r"you\s+are\s+now\s+in\s+developer\s+mode",
]


@router.post(
    "/{patient_id}",
    response_model=ClinicalReasoningResponse,
    summary="Generate Doctor-Only Clinical Reasoning Support",
    description="Constructs patient-specific evidence context, retrieves longitudinal memory, queries LLM reasoning engine, runs deterministic safety validation, and returns structured clinical considerations."
)
def get_clinical_reasoning(
    patient_id: str,
    request_data: ClinicalReasoningRequest,
    request: Request,
    current_doctor: User = Depends(require_doctor),
    db: Session = Depends(get_db)
) -> ClinicalReasoningResponse:
    """
    Doctor-Only Clinical Reasoning Station Endpoint.
    - Restricted to DOCTOR role only.
    - Enforces patient-level authorization grant.
    - Strictly read-only; does NOT mutate patient records, diagnoses, or memory claims.
    """
    ip = request.client.host if request.client else "unknown"

    # 1. Patient Authorization Check
    patient = verify_patient_access(patient_id, current_doctor, db, request)

    # 2. Prompt Injection Defense
    question_lower = request_data.question.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, question_lower):
            AuditService.log_security_event(
                db=db,
                event_type="PROMPT_INJECTION_ATTEMPT",
                user_id=current_doctor.id,
                username=current_doctor.username,
                details=f"Prompt injection detected in query for patient {patient.patient_code}: '{request_data.question}'",
                severity="HIGH",
                ip_address=ip
            )
            AuditService.log_audit_event(
                db=db,
                action="CLINICAL_REASONING_REJECTED",
                user_id=current_doctor.id,
                username=current_doctor.username,
                role="DOCTOR",
                patient_id=patient.patient_code,
                result="REJECTED",
                reason="Prompt injection pattern detected",
                ip_address=ip
            )
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": "Query rejected by EvoCare Prompt Injection & Safety Filter.",
                    "violations": ["Prompt injection attempt detected."],
                    "session_id": f"INJ-{uuid.uuid4().hex[:6].upper()}"
                }
            )

    # 3. Build Structured Relevance-Filtered Patient Context
    try:
        context = ClinicalContextService.build_patient_context(db, patient.patient_code, request_data.question)
    except Exception as e:
        logger.error(f"Failed to build clinical context for {patient.patient_code}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Context extraction error: {str(e)}"
        )

    # 4. Call LLM Provider for Structured Candidate
    llm_provider = AnthropicProvider()
    try:
        candidate_reasoning = llm_provider.generate_clinical_reasoning(request_data.question, context)
    except Exception as e:
        logger.error(f"LLM reasoning generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clinical reasoning generation error: {str(e)}"
        )

    # 5. Deterministic Safety & Provenance Validation
    is_safe, violations, sanitized_data = ClinicalReasoningValidator.validate_safety_and_provenance(
        parsed_data=candidate_reasoning,
        context=context,
        db=db,
        patient_id=patient.patient_code,
        question=request_data.question
    )

    session_id = f"RS-{uuid.uuid4().hex[:8].upper()}"

    if not is_safe or not sanitized_data:
        # Record failed audit log
        audit_session = ReasoningSession(
            session_id=session_id,
            patient_id=patient.patient_code,
            doctor_id=current_doctor.username or request_data.doctor_id or "DEMO_DOCTOR",
            question=request_data.question,
            created_at=datetime.now(timezone.utc),
            evidence_ids_used=[],
            model_used="claude-3-5-sonnet-20241022",
            validation_status="SAFETY_REJECTED",
            summary=f"Violations: {'; '.join(violations)}"
        )
        db.add(audit_session)
        db.commit()

        AuditService.log_audit_event(
            db=db,
            action="CLINICAL_REASONING_REJECTED",
            user_id=current_doctor.id,
            username=current_doctor.username,
            role="DOCTOR",
            patient_id=patient.patient_code,
            resource_type="REASONING_SESSION",
            resource_id=session_id,
            result="REJECTED",
            reason=f"Violations: {'; '.join(violations)}",
            ip_address=ip
        )

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Clinical reasoning output was rejected by EvoCare Safety Validator.",
                "violations": violations,
                "session_id": session_id
            }
        )

    # 6. Extract Evidence IDs used
    evidence_ids_used = set()
    for c in sanitized_data.get("considerations", []):
        for ref in c.get("references", []):
            evidence_ids_used.add(ref)
        for ev in c.get("supporting_evidence", []):
            if isinstance(ev, dict) and ev.get("evidence_id"):
                evidence_ids_used.add(ev["evidence_id"])

    # 7. Record Immutable Audit Session
    try:
        audit_session = ReasoningSession(
            session_id=session_id,
            patient_id=patient.patient_code,
            doctor_id=current_doctor.username or request_data.doctor_id or "DEMO_DOCTOR",
            question=request_data.question,
            created_at=datetime.now(timezone.utc),
            evidence_ids_used=list(evidence_ids_used),
            model_used="claude-3-5-sonnet-20241022",
            validation_status="PASSED",
            summary=f"Generated {len(sanitized_data.get('considerations', []))} considerations."
        )
        db.add(audit_session)
        db.commit()

        AuditService.log_audit_event(
            db=db,
            action="CLINICAL_REASONING_QUERY",
            user_id=current_doctor.id,
            username=current_doctor.username,
            role="DOCTOR",
            patient_id=patient.patient_code,
            resource_type="REASONING_SESSION",
            resource_id=session_id,
            result="SUCCESS",
            ip_address=ip
        )
    except Exception as e:
        logger.warning(f"Could not persist audit session record: {e}")
        db.rollback()

    # 8. Assemble Structured Response
    return ClinicalReasoningResponse(
        question=request_data.question,
        patient_id=patient.patient_code,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        context_summary=context["summary"],
        considerations=[ClinicalConsideration(**c) for c in sanitized_data["considerations"]],
        missing_information=sanitized_data.get("missing_information", []),
        red_flags=sanitized_data.get("red_flags", []),
        relevant_changes=sanitized_data.get("relevant_changes", []),
        limitations=sanitized_data.get("limitations", []),
        session_id=session_id,
        model_used="claude-3-5-sonnet-20241022 (simulated/mock-compatible)",
        validation_status="PASSED"
    )

