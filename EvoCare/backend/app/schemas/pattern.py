from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import InformationState
from app.schemas.evidence import EvidenceResponse

class PatternResponse(BaseModel):
    id: int
    patient_id: int
    category: str
    title: str
    description: str
    status: InformationState
    supporting_evidence_codes: List[str] = []
    detected_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PatternProvenanceResponse(BaseModel):
    pattern_id: int
    title: str
    category: str
    description: str
    status: InformationState
    detected_at: datetime
    supporting_evidence: List[EvidenceResponse]
