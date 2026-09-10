from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict

class PatientDemographics(BaseModel):
    id: int
    patient_code: str
    name: str
    age: int
    sex: str
    location: str
    dataset_type: str = "SYNTHETIC DEMO DATA"
    primary_language: str = "Tamil / English"

    model_config = ConfigDict(from_attributes=True)

class OverviewStatusItem(BaseModel):
    category: str
    baseline: str
    recent_status: str
    status_tone: str  # "neutral" | "caution" | "alert" | "info"
    source_type: str
    is_clinician_confirmed: bool

class RecentChangeItem(BaseModel):
    category: str
    title: str
    latest_state: str
    previous_state: str
    direction: str  # "IMPROVEMENT" | "DECLINE" | "FLUCTUATION" | "NEW_REPORT"
    observed_date: str
    source_type: str  # "CAREGIVER" | "DOCTOR" | "AI_DERIVED"
    information_state: str  # "RAW_OBSERVATION" | "AI_DERIVED" | "CLINICIAN_CONFIRMED"
    evidence_count: int
    evidence_ids: List[str]
    confidence: str
    change_summary: str
    memory_version: Optional[int] = None

class DiagnosisItem(BaseModel):
    code: str
    description: str
    confirmed_date: str
    doctor: str

class MedicationItem(BaseModel):
    name: str
    dose: str
    frequency: str
    status: str
    indication: str
    evidence_code: str
    start_date: Optional[str] = None

class LabResultItem(BaseModel):
    test_name: str
    value: str
    unit: str
    reference_range: str
    date: str
    evidence_code: str

class CaregiverObservationItem(BaseModel):
    id: int
    evidence_code: str
    caregiver_id: str
    category: str
    observation_text: str
    attributes: Dict[str, Any] = {}
    observed_at: str
    recorded_at: str
    information_state: str

class MemoryClaimItem(BaseModel):
    claim_code: str
    memory_page: str
    category: str
    statement: str
    information_state: str
    source_types: List[str]
    evidence_ids: List[str]
    confidence: str
    version: int

class LongitudinalMemoryPayload(BaseModel):
    current_version: int
    last_updated: str
    baseline: str
    recent_changes: str
    clinician_confirmed: str
    caregiver_reported: str
    conflicts: str
    unknowns: str
    active_claims: List[MemoryClaimItem] = []

class TimelineEventItem(BaseModel):
    id: str
    date: str
    category: str
    title: str
    description: str
    source_type: str  # "CLINICIAN-CONFIRMED", "CAREGIVER-REPORTED", "LAB", "MEDICATION"
    badge: str
    evidence_id: Optional[str] = None

class ConflictItem(BaseModel):
    id: int
    category: str
    title: str
    description: str
    doctor_view: str
    caregiver_view: str
    context: str
    status: str  # "CONTEXTUAL" | "UNRESOLVED" | "RESOLVED"
    evidence_ids: List[str]

class FallVsNearFallPayload(BaseModel):
    completed_falls_count: int = 0
    near_falls_count: int = 0
    near_fall_events: List[Dict[str, Any]] = []
    safety_rule: str = "Strict invariant: Near-falls are NEVER classified as completed falls."

class EvidenceDetailItem(BaseModel):
    evidence_code: str
    patient_id: int
    source_type: str
    observed_at: str
    recorded_at: str
    original_statement: str
    category: str
    status: str
    observer: Optional[str] = None
    linked_claims: List[str] = []

class DashboardResponse(BaseModel):
    patient: PatientDemographics
    overview: List[OverviewStatusItem]
    recent_changes: List[RecentChangeItem]
    clinical_diagnoses: List[DiagnosisItem]
    medications: List[MedicationItem]
    labs: List[LabResultItem]
    caregiver_observations: List[CaregiverObservationItem]
    longitudinal_memory: LongitudinalMemoryPayload
    timeline: List[TimelineEventItem]
    conflicts: List[ConflictItem]
    fall_safety: FallVsNearFallPayload
    provenance_map: Dict[str, EvidenceDetailItem]
