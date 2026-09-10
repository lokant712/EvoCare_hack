import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db, utc_now
from app.core.dependencies import get_current_user
from app.models.security import User, UserRole, PatientAccess, AccessRole
from app.models.patient import Patient
from app.models.caregiver_connection import CaregiverConnection, ConnectionStatus
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/caregiver-connections", tags=["Patient & Caregiver Connections"])


class CaregiverInfo(BaseModel):
    id: int
    username: str
    full_name: str
    email: str


class ConnectionRequestPayload(BaseModel):
    patient_code: str = Field(..., min_length=2)
    caregiver_user_id: int
    notes: Optional[str] = None


class ConnectionResponseItem(BaseModel):
    id: int
    patient_code: str
    patient_name: str
    caregiver_user_id: int
    caregiver_name: str
    caregiver_username: str
    caregiver_email: str
    status: str
    requested_by: str
    notes: Optional[str]
    created_at: str


class RespondPayload(BaseModel):
    action: str = Field(..., description="'APPROVE' or 'REJECT'")


@router.get("/caregivers", response_model=List[CaregiverInfo])
def get_available_caregivers(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all registered and active caregiver accounts available for pairing."""
    caregivers = db.query(User).filter(
        User.role == UserRole.CAREGIVER,
        User.is_active == True
    ).all()

    return [
        CaregiverInfo(
            id=c.id,
            username=c.username,
            full_name=c.full_name,
            email=c.email
        )
        for c in caregivers
    ]


@router.get("/my-connections", response_model=List[ConnectionResponseItem])
def get_my_connections(
    patient_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve active or pending caregiver pairings for the current user/patient."""
    role_str = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)

    query = db.query(CaregiverConnection)

    if role_str == "CAREGIVER":
        query = query.filter(CaregiverConnection.caregiver_user_id == current_user.id)
    elif patient_code:
        query = query.filter(CaregiverConnection.patient_code == patient_code.strip().upper())

    records = query.order_by(CaregiverConnection.created_at.desc()).all()

    res = []
    for r in records:
        pat = db.query(Patient).filter(Patient.patient_code == r.patient_code).first()
        cg = db.query(User).filter(User.id == r.caregiver_user_id).first()
        res.append(ConnectionResponseItem(
            id=r.id,
            patient_code=r.patient_code,
            patient_name=pat.name if pat else r.patient_code,
            caregiver_user_id=r.caregiver_user_id,
            caregiver_name=cg.full_name if cg else "Caregiver",
            caregiver_username=cg.username if cg else "caregiver",
            caregiver_email=cg.email if cg else "",
            status=r.status.value if hasattr(r.status, 'value') else str(r.status),
            requested_by=r.requested_by,
            notes=r.notes,
            created_at=r.created_at.strftime("%Y-%m-%d %H:%M:%S") if r.created_at else ""
        ))

    return res


@router.post("/request", response_model=Dict[str, Any])
def request_caregiver_connection(
    payload: ConnectionRequestPayload,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Patient selects and requests pairing with a caregiver."""
    clean_code = payload.patient_code.strip().upper()
    patient = db.query(Patient).filter(Patient.patient_code == clean_code).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient '{clean_code}' not found.")

    caregiver = db.query(User).filter(
        User.id == payload.caregiver_user_id,
        User.role == UserRole.CAREGIVER
    ).first()
    if not caregiver:
        raise HTTPException(status_code=404, detail=f"Caregiver ID {payload.caregiver_user_id} not found.")

    # Check if active connection already exists
    existing = db.query(CaregiverConnection).filter(
        CaregiverConnection.patient_code == clean_code,
        CaregiverConnection.caregiver_user_id == caregiver.id
    ).first()

    if existing:
        if existing.status == ConnectionStatus.APPROVED:
            return {
                "status": "already_approved",
                "message": f"Caregiver {caregiver.full_name} is already connected to patient {patient.name}."
            }
        existing.status = ConnectionStatus.PENDING
        existing.notes = payload.notes
        existing.updated_at = utc_now()
    else:
        new_conn = CaregiverConnection(
            patient_code=clean_code,
            caregiver_user_id=caregiver.id,
            status=ConnectionStatus.PENDING,
            requested_by="PATIENT",
            notes=payload.notes
        )
        db.add(new_conn)

    db.commit()

    ip = request.client.host if request.client else "unknown"
    AuditService.log_security_event(
        db=db,
        event_type="CAREGIVER_PAIRING_REQUESTED",
        user_id=current_user.id,
        username=current_user.username,
        details=f"Patient '{clean_code}' requested pairing with Caregiver '{caregiver.username}'",
        severity="INFO",
        ip_address=ip
    )

    return {
        "status": "success",
        "message": f"Connection request sent to caregiver {caregiver.full_name}. Awaiting approval."
    }


@router.post("/{connection_id}/respond", response_model=Dict[str, Any])
def respond_caregiver_connection(
    connection_id: int,
    payload: RespondPayload,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Caregiver Approves or Rejects an incoming patient connection request."""
    conn = db.query(CaregiverConnection).filter(CaregiverConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection request not found.")

    action = payload.action.strip().upper()
    if action not in ("APPROVE", "REJECT"):
        raise HTTPException(status_code=400, detail="Action must be 'APPROVE' or 'REJECT'.")

    ip = request.client.host if request.client else "unknown"

    if action == "APPROVE":
        conn.status = ConnectionStatus.APPROVED
        conn.updated_at = utc_now()

        # Grant persistent PatientAccess
        grant = db.query(PatientAccess).filter(
            PatientAccess.user_id == conn.caregiver_user_id,
            PatientAccess.patient_code == conn.patient_code
        ).first()

        if grant:
            grant.is_active = True
            grant.revoked_at = None
        else:
            new_grant = PatientAccess(
                user_id=conn.caregiver_user_id,
                patient_code=conn.patient_code,
                access_role=AccessRole.PRIMARY_CAREGIVER,
                granted_by="PATIENT_PAIRING_APPROVED",
                is_active=True
            )
            db.add(new_grant)

        db.commit()

        AuditService.log_security_event(
            db=db,
            event_type="CAREGIVER_PAIRING_APPROVED",
            user_id=current_user.id,
            username=current_user.username,
            details=f"Caregiver approved pairing for patient '{conn.patient_code}'. Persistent access granted.",
            severity="INFO",
            ip_address=ip
        )

        return {
            "status": "success",
            "message": f"Approved! You are now the official caretaker for patient {conn.patient_code}."
        }
    else:
        conn.status = ConnectionStatus.REJECTED
        conn.updated_at = utc_now()
        db.commit()

        AuditService.log_security_event(
            db=db,
            event_type="CAREGIVER_PAIRING_REJECTED",
            user_id=current_user.id,
            username=current_user.username,
            details=f"Caregiver rejected pairing for patient '{conn.patient_code}'.",
            severity="INFO",
            ip_address=ip
        )

        return {
            "status": "success",
            "message": f"Connection request for patient {conn.patient_code} has been rejected."
        }


@router.post("/{connection_id}/disconnect", response_model=Dict[str, Any])
def disconnect_caregiver_connection(
    connection_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove / disconnect patient-caregiver relationship."""
    conn = db.query(CaregiverConnection).filter(CaregiverConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(status_code=404, detail="Connection not found.")

    conn.status = ConnectionStatus.DISCONNECTED
    conn.updated_at = utc_now()

    # Revoke patient access grant
    grant = db.query(PatientAccess).filter(
        PatientAccess.user_id == conn.caregiver_user_id,
        PatientAccess.patient_code == conn.patient_code
    ).first()

    if grant:
        grant.is_active = False
        grant.revoked_at = utc_now()

    db.commit()

    ip = request.client.host if request.client else "unknown"
    AuditService.log_security_event(
        db=db,
        event_type="CAREGIVER_PAIRING_DISCONNECTED",
        user_id=current_user.id,
        username=current_user.username,
        details=f"Pairing between Caregiver ID {conn.caregiver_user_id} and Patient '{conn.patient_code}' disconnected.",
        severity="INFO",
        ip_address=ip
    )

    return {
        "status": "success",
        "message": f"Caregiver pairing for patient {conn.patient_code} has been removed."
    }
