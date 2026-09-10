from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class LabRecord(Base):
    __tablename__ = "lab_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), nullable=False, index=True)
    test_panel = Column(String(255), nullable=False)
    test_name = Column(String(255), nullable=False, index=True)
    value = Column(String(100), nullable=False)
    unit = Column(String(50), nullable=True)
    reference_range = Column(String(100), nullable=True)
    observed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="lab_records")
    evidence = relationship("Evidence", back_populates="lab_records")
