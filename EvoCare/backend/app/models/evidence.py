from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base, utc_now
from app.models.enums import SourceType, EvidenceStatus
from app.models.associations import pattern_evidence_association, conflict_evidence_association, baseline_evidence_association

class Evidence(Base):
    __tablename__ = "evidences"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_code = Column(String(50), unique=True, index=True, nullable=False)
    source_type = Column(SQLEnum(SourceType), nullable=False, index=True)
    source_id = Column(String(100), nullable=False)
    observed_at = Column(DateTime, nullable=False, index=True)
    recorded_at = Column(DateTime, nullable=False)
    original_statement = Column(Text, nullable=False)
    status = Column(SQLEnum(EvidenceStatus), default=EvidenceStatus.IMMUTABLE, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="evidences")
    observations = relationship("Observation", back_populates="evidence")
    caregiver_observations = relationship("CaregiverObservation", back_populates="evidence")
    doctor_records = relationship("DoctorRecord", back_populates="evidence")
    medications = relationship("Medication", back_populates="evidence")
    lab_records = relationship("LabRecord", back_populates="evidence")
    patterns = relationship("Pattern", secondary=pattern_evidence_association, back_populates="supporting_evidences")
    conflicts = relationship("Conflict", secondary=conflict_evidence_association, back_populates="supporting_evidences")
    baselines = relationship("Baseline", secondary=baseline_evidence_association, back_populates="supporting_evidences")
