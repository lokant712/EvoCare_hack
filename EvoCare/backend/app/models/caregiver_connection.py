import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
from app.core.database import Base, utc_now


class ConnectionStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISCONNECTED = "DISCONNECTED"


class CaregiverConnection(Base):
    __tablename__ = "caregiver_connections"

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), nullable=False, index=True)
    caregiver_user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(ConnectionStatus), default=ConnectionStatus.PENDING, nullable=False)
    requested_by = Column(String(50), default="PATIENT", nullable=False)  # "PATIENT" or "CAREGIVER"
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    caregiver = relationship("User", foreign_keys=[caregiver_user_id])
