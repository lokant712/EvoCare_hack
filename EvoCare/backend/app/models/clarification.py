import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base

class SessionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ClarificationSession(Base):
    __tablename__ = "clarification_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    detected_category = Column(String(100), nullable=False, index=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.PENDING, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    resulting_evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    patient = relationship("Patient")
    resulting_evidence = relationship("Evidence")
    questions = relationship("ClarificationQuestion", back_populates="session", cascade="all, delete-orphan", order_by="ClarificationQuestion.id")
    answers = relationship("ClarificationAnswer", back_populates="session", cascade="all, delete-orphan")

class ClarificationQuestion(Base):
    __tablename__ = "clarification_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("clarification_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    field_name = Column(String(100), nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    options = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ClarificationSession", back_populates="questions")
    answers = relationship("ClarificationAnswer", back_populates="question", cascade="all, delete-orphan")

class ClarificationAnswer(Base):
    __tablename__ = "clarification_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("clarification_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("clarification_questions.id", ondelete="CASCADE"), nullable=True, index=True)
    field_name = Column(String(100), nullable=False)
    answer = Column(Text, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ClarificationSession", back_populates="answers")
    question = relationship("ClarificationQuestion", back_populates="answers")
