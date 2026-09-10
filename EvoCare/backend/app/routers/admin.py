import logging
import random
import string
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.dependencies import require_admin
from app.models.security import User, PatientAccess, SecurityEvent
from app.models.audit import AuditLog
from app.services.audit_service import AuditService

# In-memory OTP store: { user_id: otp_string }
# In production this would be Redis with TTL
_otp_store: Dict[int, str] = {}

def _generate_otp() -> str:
    return ''.join(random.choices(string.digits, k=6))

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
            "is_verified": getattr(u, 'is_verified', True),
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


@router.post("/users", status_code=201)
def create_user(
    payload: Dict[str, Any],
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new system user (ADMIN only)."""
    from app.core.security import get_password_hash
    from app.models.security import UserRole

    username = payload.get("username", "").strip()
    password = payload.get("password", "").strip()
    full_name = payload.get("full_name", "").strip()
    email = payload.get("email", "").strip()
    role_str = payload.get("role", "DOCTOR").upper()
    patient_code = payload.get("patient_code", "").strip() or None

    if not username or not password or not full_name or not email:
        raise HTTPException(status_code=400, detail="username, password, full_name and email are required.")

    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=409, detail=f"Username '{username}' already exists.")
    if db.query(User).filter(User.email == email).first():
        raise HTTPException(status_code=409, detail=f"Email '{email}' already registered.")

    try:
        role_enum = UserRole(role_str)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid role '{role_str}'. Must be DOCTOR, CAREGIVER, PATIENT, or ADMIN.")

    new_user = User(
        username=username,
        email=email,
        password_hash=get_password_hash(password),
        full_name=full_name,
        role=role_enum,
        is_active=True,
        is_verified=False,  # requires email verification by admin
    )
    db.add(new_user)
    db.flush()

    # Auto-grant patient access if patient_code provided
    if patient_code:
        access_role_map = {
            "DOCTOR": "ATTENDING_PHYSICIAN",
            "CAREGIVER": "PRIMARY_CAREGIVER",
            "PATIENT": "PATIENT_SELF",
        }
        grant = PatientAccess(
            user_id=new_user.id,
            patient_code=patient_code,
            access_role=access_role_map.get(role_str, "ATTENDING_PHYSICIAN"),
            granted_by=current_admin.username,
            is_active=True,
        )
        db.add(grant)

    db.commit()
    db.refresh(new_user)

    # Generate OTP for email verification
    otp = _generate_otp()
    _otp_store[new_user.id] = otp

    AuditService.log_audit_event(
        db=db, action="USER_CREATED", user_id=current_admin.id,
        username=current_admin.username, role="ADMIN",
        patient_id=patient_code or "N/A", resource_type="USER",
        resource_id=str(new_user.id), result="SUCCESS",
        details={"new_username": username, "role": role_str}
    )

    return {
        "id": new_user.id, "username": new_user.username,
        "full_name": new_user.full_name, "email": new_user.email,
        "role": new_user.role.value, "is_active": new_user.is_active,
        "is_verified": new_user.is_verified,
        "patient_code": patient_code,
        "verification_otp": otp,  # In prod: this would be emailed; here shown to admin
        "otp_message": f"Share this OTP with {new_user.full_name} ({new_user.email}) to verify their account."
    }


@router.patch("/users/{user_id}/toggle")
def toggle_user_active(
    user_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Enable or disable a user account (ADMIN only). Cannot disable own account."""
    if user_id == current_admin.id:
        raise HTTPException(status_code=400, detail="Cannot disable your own account.")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    target.is_active = not target.is_active
    db.commit()
    db.refresh(target)

    action = "USER_ENABLED" if target.is_active else "USER_DISABLED"
    AuditService.log_audit_event(
        db=db, action=action, user_id=current_admin.id,
        username=current_admin.username, role="ADMIN",
        patient_id="N/A", resource_type="USER",
        resource_id=str(user_id), result="SUCCESS",
        details={"target_username": target.username, "new_status": target.is_active}
    )

    return {
        "id": target.id, "username": target.username,
        "is_active": target.is_active,
        "message": f"Account {'enabled' if target.is_active else 'disabled'} successfully."
    }


@router.post("/users/{user_id}/verify")
def verify_user(
    user_id: int,
    payload: Dict[str, Any],
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Verify a user account using OTP (ADMIN only).
    Admin enters the OTP they shared with the user; if it matches, the user is marked verified.
    """
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")

    entered_otp = str(payload.get("otp", "")).strip()
    stored_otp = _otp_store.get(user_id)

    if not stored_otp:
        raise HTTPException(status_code=400, detail="No pending OTP for this user. Use resend-otp to generate a new one.")

    if entered_otp != stored_otp:
        raise HTTPException(status_code=400, detail="Incorrect OTP. Please try again or resend.")

    target.is_verified = True
    db.commit()
    db.refresh(target)

    # Consume OTP after successful verification
    _otp_store.pop(user_id, None)

    AuditService.log_audit_event(
        db=db, action="USER_VERIFIED", user_id=current_admin.id,
        username=current_admin.username, role="ADMIN",
        patient_id="N/A", resource_type="USER",
        resource_id=str(user_id), result="SUCCESS",
        details={"verified_username": target.username}
    )

    return {
        "id": target.id, "username": target.username,
        "is_verified": target.is_verified,
        "message": f"Account '{target.username}' successfully verified."
    }


@router.post("/users/{user_id}/resend-otp")
def resend_otp(
    user_id: int,
    current_admin: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Generate and return a fresh OTP for a user (ADMIN only)."""
    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found.")
    if getattr(target, 'is_verified', False):
        raise HTTPException(status_code=400, detail="User is already verified.")

    otp = _generate_otp()
    _otp_store[user_id] = otp

    return {
        "id": user_id,
        "username": target.username,
        "email": target.email,
        "verification_otp": otp,
        "otp_message": f"New OTP generated. Share with {target.full_name} ({target.email})."
    }

