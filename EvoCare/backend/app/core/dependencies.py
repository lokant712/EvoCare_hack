import logging
from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.security import decode_token, is_token_revoked
from app.models.security import User, UserRole, PatientAccess
from app.models.patient import Patient
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Validates JWT access token and retrieves active user from database.
    If AUTH_ENABLED is False and DEMO_MODE is True, returns default demo doctor.
    """
    token: Optional[str] = None
    if credentials:
        token = credentials.credentials
    else:
        # Fallback to query param or custom header if needed
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        if not settings.AUTH_ENABLED and settings.DEMO_MODE:
            # Fallback for offline unauthenticated demo if explicitly configured
            demo_user = db.query(User).filter(User.username == "doctor.demo").first()
            if demo_user:
                return demo_user

        # Record unauthorized access attempt
        ip = request.client.host if request.client else "unknown"
        AuditService.log_security_event(
            db=db,
            event_type="UNAUTHENTICATED_ACCESS_ATTEMPT",
            details=f"Unauthenticated request to {request.url.path}",
            severity="MEDIUM",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a valid Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_token(token)
    except ValueError as e:
        ip = request.client.host if request.client else "unknown"
        AuditService.log_security_event(
            db=db,
            event_type="INVALID_TOKEN_ATTEMPT",
            details=f"Token validation failed: {str(e)} at {request.url.path}",
            severity="HIGH",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload claims.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account no longer exists.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account has been deactivated.",
        )

    return user


def require_authenticated_user(current_user: User = Depends(get_current_user)) -> User:
    """Dependency ensuring an authenticated user is present."""
    return current_user


def require_role(*roles: UserRole):
    """Dependency factory enforcing that current user has one of the required roles."""
    def role_checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ) -> User:
        user_role = current_user.role
        if isinstance(user_role, str):
            user_role = UserRole(user_role)

        allowed_role_values = [r.value if isinstance(r, UserRole) else r for r in roles]
        if user_role.value not in allowed_role_values:
            ip = request.client.host if request.client else "unknown"
            AuditService.log_security_event(
                db=db,
                event_type="RBAC_ROLE_DENIED",
                user_id=current_user.id,
                username=current_user.username,
                details=f"User with role '{user_role.value}' attempted to access endpoint requiring {allowed_role_values} at {request.url.path}",
                severity="HIGH",
                ip_address=ip
            )
            AuditService.log_audit_event(
                db=db,
                action="ROLE_ACCESS_DENIED",
                user_id=current_user.id,
                username=current_user.username,
                role=user_role.value,
                result="DENIED",
                reason=f"Requires one of {allowed_role_values}",
                ip_address=ip
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Role '{user_role.value}' does not possess required permissions for this action."
            )
        return current_user

    return role_checker


def require_doctor(current_user: User = Depends(require_role(UserRole.DOCTOR))) -> User:
    """Dependency requiring DOCTOR role."""
    return current_user


def require_caregiver(current_user: User = Depends(require_role(UserRole.CAREGIVER))) -> User:
    """Dependency requiring CAREGIVER role."""
    return current_user


def require_admin(current_user: User = Depends(require_role(UserRole.ADMIN))) -> User:
    """Dependency requiring ADMIN role."""
    return current_user


def verify_patient_access(
    patient_id: str,
    user: User,
    db: Session,
    request: Optional[Request] = None
) -> Patient:
    """
    Core function to verify patient-level access.
    Returns Patient instance if access is granted, otherwise raises 403.
    """
    # Normalize patient code / ID
    patient = db.query(Patient).filter(
        (Patient.patient_code == patient_id) |
        (Patient.id == (int(patient_id) if patient_id.isdigit() else -1))
    ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient '{patient_id}' not found."
        )

    # Check PatientAccess grant
    has_grant = db.query(PatientAccess).filter(
        PatientAccess.user_id == user.id,
        PatientAccess.patient_code == patient.patient_code,
        PatientAccess.is_active == True
    ).first()

    if not has_grant:
        ip = request.client.host if request and request.client else "unknown"
        AuditService.log_security_event(
            db=db,
            event_type="UNAUTHORIZED_PATIENT_ACCESS",
            user_id=user.id,
            username=user.username,
            details=f"User '{user.username}' ({user.role}) attempted unauthorized access to patient '{patient.patient_code}'",
            severity="HIGH",
            ip_address=ip
        )
        AuditService.log_audit_event(
            db=db,
            action="PATIENT_ACCESS_DENIED",
            user_id=user.id,
            username=user.username,
            role=user.role.value if hasattr(user.role, 'value') else str(user.role),
            patient_id=patient.patient_code,
            result="DENIED",
            reason=f"No active access grant for patient {patient.patient_code}",
            ip_address=ip
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You are not authorized to view or access records for patient '{patient_id}'."
        )

    return patient
