import logging
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.security import User, PatientAccess, SecurityEvent
from app.models.audit import AuditLog
from app.services.audit_service import AuditService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Administrative & Security Monitoring"])


@router.get("/audit-logs")
def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve system audit logs (ADMIN only). Does NOT expose raw medical records."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    
    logs = query.order_by(desc(AuditLog.timestamp)).limit(limit).all()
    return [
        {
            "id": l.id,
            "event_id": l.event_id,
            "username": l.username,
            "role": l.role,
            "patient_id": l.patient_id,
            "action": l.action,
            "resource_type": l.resource_type,
            "resource_id": l.resource_id,
            "result": l.result,
            "reason": l.reason,
            "ip_address": l.ip_address,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if l.timestamp else None,
            "details": l.details
        }
        for l in logs
    ]


@router.get("/security-events")
def get_security_events(
    limit: int = Query(50, ge=1, le=200),
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Retrieve security violation alarms (ADMIN only)."""
    events = db.query(SecurityEvent).order_by(desc(SecurityEvent.timestamp)).limit(limit).all()
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "username": e.username,
            "severity": e.severity,
            "details": e.details,
            "ip_address": e.ip_address,
            "timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC") if e.timestamp else None
        }
        for e in events
    ]


@router.get("/users")
def get_user_management_list(
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """List system users and their active patient access grants (ADMIN only)."""
    users = db.query(User).all()
    result = []
    for u in users:
        grants = db.query(PatientAccess).filter(PatientAccess.user_id == u.id, PatientAccess.is_active == True).all()
        result.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "full_name": u.full_name,
            "role": u.role.value if hasattr(u.role, 'value') else str(u.role),
            "is_active": u.is_active,
            "created_at": u.created_at.strftime("%Y-%m-%d %H:%M") if u.created_at else None,
            "last_login_at": u.last_login_at.strftime("%Y-%m-%d %H:%M") if u.last_login_at else None,
            "authorized_patients": [g.patient_code for g in grants]
        })
    return result


@router.post("/grants")
def create_patient_access_grant(
    payload: Dict[str, Any],
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Grant patient access to a user (ADMIN only)."""
    user_id = payload.get("user_id")
    patient_code = payload.get("patient_code")
    access_role = payload.get("access_role", "ATTENDING_PHYSICIAN")


    if not user_id or not patient_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id and patient_code are required."
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {user_id} not found.")

    # Check if active grant exists
    existing = db.query(PatientAccess).filter(
        PatientAccess.user_id == user_id,
        PatientAccess.patient_code == patient_code,
        PatientAccess.is_active == True
    ).first()

    if existing:
        return {"status": "exists", "message": f"User already has active access to {patient_code}", "grant_id": existing.id}

    grant = PatientAccess(
        user_id=user_id,
        patient_code=patient_code,
        access_role=access_role,
        is_active=True
    )
    db.add(grant)
    db.commit()
    db.refresh(grant)

    AuditService.log_audit_event(
        db=db,
        action="GRANT_CREATED",
        user_id=current_admin.id,
        username=current_admin.username,
        role="ADMIN",
        patient_id=patient_code,
        resource_type="PATIENT_ACCESS",
        resource_id=str(grant.id),
        result="SUCCESS",
        details={"granted_to_user_id": user_id, "granted_to_username": user.username}
    )

    return {"status": "success", "grant_id": grant.id, "patient_code": patient_code, "username": user.username}


@router.delete("/grants/{grant_id}")
def revoke_patient_access_grant(
    grant_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Revoke a patient access grant (ADMIN only)."""
    grant = db.query(PatientAccess).filter(PatientAccess.id == grant_id).first()
    if not grant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grant {grant_id} not found.")

    grant.is_active = False
    db.commit()

    AuditService.log_audit_event(
        db=db,
        action="GRANT_REVOKED",
        user_id=current_admin.id,
        username=current_admin.username,
        role="ADMIN",
        patient_id=grant.patient_code,
        resource_type="PATIENT_ACCESS",
        resource_id=str(grant.id),
        result="SUCCESS",
        details={"revoked_user_id": grant.user_id}
    )

    return {"status": "success", "message": f"Grant {grant_id} revoked."}

