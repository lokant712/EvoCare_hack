from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class DoctorRecordResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    doctor_id: str
    source_type: str = "DOCTOR"
    record_type: str
    content: str
    observed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
