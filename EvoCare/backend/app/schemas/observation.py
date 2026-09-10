from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import InformationState

class ObservationBase(BaseModel):
    category: str
    status: InformationState = InformationState.OBSERVED
    observed_at: datetime
    severity: Optional[str] = None
    duration: Optional[str] = None
    onset: Optional[str] = None
    frequency: Optional[str] = None
    comparison_to_baseline: Optional[str] = None
    time_context: Optional[str] = None
    confidence: Optional[str] = None
    clarification_required: bool = False

class ObservationResponse(ObservationBase):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: Optional[str] = None
    source_type: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
