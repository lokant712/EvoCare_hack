from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.enums import InformationState

class CaregiverObservationResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    caregiver_id: str
    source_type: str = "CAREGIVER"
    category: str
    observation_text: str
    attributes: Optional[Dict[str, Any]] = None
    observed_at: datetime
    information_state: InformationState
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
