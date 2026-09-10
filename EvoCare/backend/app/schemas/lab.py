from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict

class LabRecordResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    source_type: str = "LAB_RECORD"
    test_panel: str
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    observed_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class LabPanelItem(BaseModel):
    test_name: str
    value: str
    unit: Optional[str] = None
    reference_range: Optional[str] = None

class LabPanelResponse(BaseModel):
    observed_at: datetime
    evidence_code: str
    test_panel: str
    biomarkers: list[LabPanelItem]
