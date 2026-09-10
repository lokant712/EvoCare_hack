import uuid
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.security import SecurityEvent

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log_audit_event(
        db: Session,
        action: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        role: Optional[str] = None,
        patient_id: Optional[str] = None,
        resource_type: str = "GENERAL",
        resource_id: Optional[str] = None,
        result: str = "SUCCESS",  # SUCCESS, DENIED, ERROR
        reason: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> AuditLog:
        """Create and persist an immutable audit trail entry."""
        import json
        meta = metadata or {}
        details_str = json.dumps(details) if isinstance(details, dict) else (str(details) if details else "")

        audit_entry = AuditLog(
            action=action,
            user_id=user_id,
            username=username or "ANONYMOUS",
            role=role,
            patient_id=patient_id,
            resource_type=resource_type,
            resource_id=resource_id,
            entity_type=resource_type,
            entity_id=resource_id or patient_id or "N/A",
            ip_address=ip_address,
            user_agent=user_agent,
            result=result,
            reason=reason,
            details=details_str,
            metadata_json=meta,
            correlation_id=correlation_id or str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc)
        )
        try:
            db.add(audit_entry)
            db.commit()
            db.refresh(audit_entry)
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")
            db.rollback()
        return audit_entry


    @staticmethod
    def log_security_event(
        db: Session,
        event_type: str,
        user_id: Optional[int] = None,
        username: Optional[str] = None,
        details: str = "",
        severity: str = "MEDIUM",  # LOW, MEDIUM, HIGH, CRITICAL
        ip_address: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SecurityEvent:
        """Record a security violation or alarm event."""
        sec_event = SecurityEvent(
            event_type=event_type,
            user_id=user_id,
            username=username or "ANONYMOUS",
            details=details,
            severity=severity,
            ip_address=ip_address,
            metadata_json=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        try:
            db.add(sec_event)
            db.commit()
            db.refresh(sec_event)
        except Exception as e:
            logger.error(f"Failed to record security event: {e}")
            db.rollback()
        return sec_event
