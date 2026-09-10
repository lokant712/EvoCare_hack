from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base

class DoctorRecord(Base):
    __tablename__ = "doctor_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), nullable=False, index=True)
    doctor_id = Column(String(100), nullable=False, index=True)
    record_type = Column(String(100), nullable=False)  # consultation, follow_up, assessment, historical_note
    content = Column(Text, nullable=False)
    observed_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    patient = relationship("Patient", back_populates="doctor_records")
    evidence = relationship("Evidence", back_populates="doctor_records")
