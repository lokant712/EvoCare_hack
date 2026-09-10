from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from app.models.enums import ConflictStatus
from app.schemas.evidence import EvidenceResponse

class ConflictResponse(BaseModel):
    id: int
    patient_id: int
    category: str
    title: str
    description: str
    doctor_view: str
    caregiver_view: str
    status: ConflictStatus
    supporting_evidence_codes: List[str] = []
    created_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class ConflictProvenanceResponse(BaseModel):
    conflict_id: int
    title: str
    category: str
    description: str
    doctor_view: str
    caregiver_view: str
    status: ConflictStatus
    supporting_evidence: List[EvidenceResponse]
