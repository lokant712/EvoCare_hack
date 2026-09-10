from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import ConflictStatus
from app.models.associations import conflict_evidence_association

class Conflict(Base):
    __tablename__ = "conflicts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    doctor_view = Column(Text, nullable=False)
    caregiver_view = Column(Text, nullable=False)
    status = Column(SQLEnum(ConflictStatus), default=ConflictStatus.CONFLICTING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    patient = relationship("Patient", back_populates="conflicts")
    supporting_evidences = relationship("Evidence", secondary=conflict_evidence_association, back_populates="conflicts")
