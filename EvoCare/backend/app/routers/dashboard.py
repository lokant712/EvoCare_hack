from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, verify_patient_access
from app.models.security import User
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import DashboardService
from app.services.audit_service import AuditService

router = APIRouter(prefix="/dashboard", tags=["Doctor Dashboard"])


@router.get("/patients/{patient_id}", response_model=DashboardResponse, summary="Get Aggregated Patient Dashboard")
def get_patient_dashboard(
    patient_id: str,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns the comprehensive longitudinal doctor dashboard view for an authorized patient:
    - Enforces authentication + patient authorization
    - Logs DASHBOARD_VIEW audit event
    """
    # Verify patient authorization
    patient = verify_patient_access(patient_id, current_user, db, request)

    # Log audit event
    ip = request.client.host if request.client else "unknown"
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    AuditService.log_audit_event(
        db=db,
        action="DASHBOARD_VIEW",
        user_id=current_user.id,
        username=current_user.username,
        role=role_str,
        patient_id=patient.patient_code,
        resource_type="DASHBOARD",
        resource_id=patient.patient_code,
        result="SUCCESS",
        ip_address=ip
    )

    return DashboardService.get_patient_dashboard(db, patient.patient_code)
