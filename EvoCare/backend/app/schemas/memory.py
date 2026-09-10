from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.baseline import BaselineResponse
from app.schemas.pattern import PatternResponse
from app.schemas.conflict import ConflictResponse
from app.schemas.medication import MedicationResponse
from app.schemas.lab import LabRecordResponse

class TimelineEventResponse(BaseModel):
    observed_at: datetime
    event_type: str
    source_type: str
    source_id: str
    description: str
    evidence_code: str
    category: Optional[str] = None
    clarification_required: bool = False

class ClinicalSummaryResponse(BaseModel):
    diagnoses: List[Dict[str, Any]]
    doctor_records: List[Dict[str, Any]]
    medical_history: List[Dict[str, Any]]
    labs: List[LabRecordResponse]
    medications: List[MedicationResponse]

class MemoryResponse(BaseModel):
    patient_id: int
    patient_code: str
    patient_name: str
    executive_summary: str
    baseline: List[BaselineResponse]
    active_patterns: List[PatternResponse]
    unresolved_conflicts: List[ConflictResponse]
    recent_improvements: List[Dict[str, Any]]
    unknown_information: List[Dict[str, Any]]
