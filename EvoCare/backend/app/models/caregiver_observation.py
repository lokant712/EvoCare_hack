from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base, utc_now
from app.models.enums import InformationState

class CaregiverObservation(Base):
    __tablename__ = "caregiver_observations"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), nullable=False, index=True)
    caregiver_id = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    observation_text = Column(Text, nullable=False)
    attributes = Column(JSON, nullable=True)
    observed_at = Column(DateTime, nullable=False, index=True)
    information_state = Column(SQLEnum(InformationState), default=InformationState.OBSERVED, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    patient = relationship("Patient", back_populates="caregiver_observations")
    evidence = relationship("Evidence", back_populates="caregiver_observations")
