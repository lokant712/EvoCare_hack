from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from app.core.database import Base, utc_now


class ReasoningSession(Base):
    __tablename__ = "reasoning_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    patient_id = Column(String(50), index=True, nullable=False)
    doctor_id = Column(String(100), default="DEMO_DOCTOR", nullable=False)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    evidence_ids_used = Column(JSON, default=list, nullable=False)
    model_used = Column(String(100), nullable=True)
    validation_status = Column(String(50), default="PASSED", nullable=False)
    summary = Column(Text, nullable=True)
