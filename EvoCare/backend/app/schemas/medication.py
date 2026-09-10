from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class MedicationResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    source_type: str = "MEDICATION_RECORD"
    name: str
    dose: str
    frequency: str
    status: str
    indication: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
