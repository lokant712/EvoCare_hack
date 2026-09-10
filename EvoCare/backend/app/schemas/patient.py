from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.baseline import BaselineResponse
from app.schemas.pattern import PatternResponse
from app.schemas.conflict import ConflictResponse
from app.schemas.medication import MedicationResponse
from app.schemas.caregiver_observation import CaregiverObservationResponse

class PatientBase(BaseModel):
    patient_code: str
    name: str
    age: int
    sex: str
    location: str
    status: str = "ACTIVE"
    is_synthetic: bool = True

class PatientResponse(PatientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PatientSummaryResponse(BaseModel):
    patient: PatientResponse
    baseline: List[BaselineResponse]
    current_diagnoses: List[str]
    active_medications: List[MedicationResponse]
    recent_observations: List[CaregiverObservationResponse]
    recent_patterns: List[PatternResponse]
    recent_conflicts: List[ConflictResponse]
