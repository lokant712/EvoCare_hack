from typing import List, Optional
from pydantic import BaseModel, Field


class DiagnosisEntryItem(BaseModel):
    condition: str = Field(..., description="Condition or diagnosis name, e.g. Orthostatic Hypotension")
    icd_code: Optional[str] = Field(None, description="ICD-10 code, e.g. I95.1")
    status: str = Field("CONFIRMED", description="Diagnosis status: CONFIRMED, SUSPECTED, DIFFERENTIAL, RESOLVED")
    notes: Optional[str] = Field(None, description="Clinical reasoning and diagnostic rationale")


class PrescriptionEntryItem(BaseModel):
    medication_name: str = Field(..., description="Name of prescribed medication, e.g. Meclizine")
    dose: str = Field(..., description="Dosage, e.g. 25 mg")
    frequency: str = Field(..., description="Frequency of intake, e.g. Once daily in morning")
    indication: Optional[str] = Field(None, description="Clinical indication, e.g. Positional dizziness")
    instructions: Optional[str] = Field(None, description="Specific instructions for patient/caregiver")


class DoctorEntryBatchRequest(BaseModel):
    consultation_title: Optional[str] = Field("Clinical Evaluation & Treatment Plan", description="Title of clinical encounter")
    clinical_notes: Optional[str] = Field(None, description="General examination observations and notes")
    diagnoses: List[DiagnosisEntryItem] = Field(default_factory=list, description="List of structured diagnoses")
    prescriptions: List[PrescriptionEntryItem] = Field(default_factory=list, description="List of structured prescriptions")


class DoctorEntryBatchResponse(BaseModel):
    success: bool
    message: str
    doctor_id: str
    patient_code: str
    recorded_at: str
    diagnoses_recorded: int
    prescriptions_recorded: int
    evidence_codes_generated: List[str]
    markdown_content: str
    markdown_file_path: Optional[str] = None
