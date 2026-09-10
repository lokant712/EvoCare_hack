import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base

class MemoryVersion(Base):
    __tablename__ = "memory_versions"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_page = Column(String(100), nullable=False, index=True)
    version_number = Column(Integer, nullable=False, index=True)
    previous_version_id = Column(Integer, ForeignKey("memory_versions.id", ondelete="SET NULL"), nullable=True)
    update_type = Column(String(50), nullable=False)  # NEW_CLAIM, CONFIRM_CLAIM, TEMPORAL_UPDATE, CONFLICT, OUTDATED, NO_CHANGE
    change_summary = Column(Text, nullable=False)
    content_snapshot = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(50), default="SYSTEM", nullable=False)
    validation_status = Column(String(50), default="APPLIED", nullable=False)

    patient = relationship("Patient")
    previous_version = relationship("MemoryVersion", remote_side=[id])

class MemoryClaim(Base):
    __tablename__ = "memory_claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    memory_page = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    statement = Column(Text, nullable=False)
    information_state = Column(String(50), default="AI_DERIVED", nullable=False)  # OBSERVED, CLINICIAN_CONFIRMED, AI_DERIVED, HISTORICAL, OUTDATED, CONFLICTING, UNKNOWN
    source_types = Column(JSON, nullable=False)  # e.g. ["CAREGIVER"], ["DOCTOR"]
    evidence_ids = Column(JSON, nullable=False)  # e.g. ["EV-CG-021"]
    confidence = Column(String(20), default="HIGH", nullable=False)
    first_observed_at = Column(DateTime, nullable=False)
    last_observed_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    active = Column(Boolean, default=True, nullable=False)

    patient = relationship("Patient")

class MemoryProposal(Base):
    __tablename__ = "memory_proposals"

    id = Column(Integer, primary_key=True, index=True)
    proposal_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="RESTRICT"), nullable=True)
    evidence_code = Column(String(50), nullable=True)
    memory_page = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    update_type = Column(String(50), nullable=False)
    proposed_claim = Column(Text, nullable=False)
    information_state = Column(String(50), default="AI_DERIVED", nullable=False)
    evidence_ids = Column(JSON, nullable=False)
    confidence = Column(String(20), default="HIGH", nullable=False)
    status = Column(String(50), default="CREATED", nullable=False)  # CREATED, VALIDATED, REJECTED, APPLIED
    validation_errors = Column(JSON, default=list, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    applied_at = Column(DateTime, nullable=True)
    resulting_version_id = Column(Integer, ForeignKey("memory_versions.id", ondelete="SET NULL"), nullable=True)

    patient = relationship("Patient")
    evidence = relationship("Evidence")
    resulting_version = relationship("MemoryVersion")
