from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base, utc_now


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True, nullable=True)
    user_id = Column(Integer, nullable=True, index=True)
    username = Column(String(100), nullable=True, index=True)
    role = Column(String(50), nullable=True, index=True)
    patient_id = Column(String(50), nullable=True, index=True)
    action = Column(String(100), nullable=False, index=True)  # LOGIN_SUCCESS, DASHBOARD_VIEW, etc.
    resource_type = Column(String(100), default="GENERAL", nullable=False)
    resource_id = Column(String(100), nullable=True)
    entity_type = Column(String(100), nullable=True)  # Legacy compatibility
    entity_id = Column(String(100), nullable=True)    # Legacy compatibility
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    result = Column(String(50), default="SUCCESS", nullable=False)  # SUCCESS, DENIED, ERROR
    reason = Column(Text, nullable=True)
    details = Column(Text, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    correlation_id = Column(String(100), nullable=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False, index=True)
