from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import SourceType, EvidenceStatus

class EvidenceBase(BaseModel):
    evidence_code: str
    source_type: SourceType
    source_id: str
    observed_at: datetime
    recorded_at: datetime
    original_statement: str
    status: EvidenceStatus = EvidenceStatus.IMMUTABLE

class EvidenceResponse(EvidenceBase):
    id: int
    patient_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EvidenceFilter(BaseModel):
    source_type: Optional[SourceType] = None
    category: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
