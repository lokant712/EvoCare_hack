from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import InformationState
from app.schemas.evidence import EvidenceResponse

class BaselineResponse(BaseModel):
    id: int
    patient_id: int
    category: str
    baseline_value: str
    information_state: InformationState
    supporting_evidence_codes: List[str] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
