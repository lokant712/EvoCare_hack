from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import InformationState

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    status = Column(SQLEnum(InformationState), default=InformationState.OBSERVED, nullable=False)
    observed_at = Column(DateTime, nullable=False, index=True)
    severity = Column(String(100), nullable=True)
    duration = Column(String(100), nullable=True)
    onset = Column(String(100), nullable=True)
    frequency = Column(String(100), nullable=True)
    comparison_to_baseline = Column(String(255), nullable=True)
    time_context = Column(String(100), nullable=True)
    confidence = Column(String(50), nullable=True)
    clarification_required = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="observations")
    evidence = relationship("Evidence", back_populates="observations")
