from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship

from app.core.database import Base, utc_now

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    age = Column(Integer, nullable=False)
    sex = Column(String(20), nullable=False)
    location = Column(String(255), nullable=False)
    status = Column(String(50), default="ACTIVE", nullable=False)
    is_synthetic = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    evidences = relationship("Evidence", back_populates="patient", cascade="all, delete-orphan")
    observations = relationship("Observation", back_populates="patient", cascade="all, delete-orphan")
    caregiver_observations = relationship("CaregiverObservation", back_populates="patient", cascade="all, delete-orphan")
    doctor_records = relationship("DoctorRecord", back_populates="patient", cascade="all, delete-orphan")
    medications = relationship("Medication", back_populates="patient", cascade="all, delete-orphan")
    lab_records = relationship("LabRecord", back_populates="patient", cascade="all, delete-orphan")
    baselines = relationship("Baseline", back_populates="patient", cascade="all, delete-orphan")
    patterns = relationship("Pattern", back_populates="patient", cascade="all, delete-orphan")
    conflicts = relationship("Conflict", back_populates="patient", cascade="all, delete-orphan")
    memory_pages = relationship("MemoryPage", back_populates="patient", cascade="all, delete-orphan")
