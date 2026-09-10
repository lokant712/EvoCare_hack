from datetime import datetime, timezone
from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ConsiderationStatus(str, Enum):
    POSSIBLE_CONSIDERATION = "POSSIBLE_CONSIDERATION"
    CLINICIAN_CONFIRMED = "CLINICIAN_CONFIRMED"
    ALREADY_CONSIDERED = "ALREADY_CONSIDERED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    NOT_SUPPORTED = "NOT_SUPPORTED"


class EvidenceStrength(str, Enum):
    STRONG = "STRONG"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"
    INSUFFICIENT = "INSUFFICIENT"


class SourceType(str, Enum):
    CLINICIAN_CONFIRMED = "CLINICIAN-CONFIRMED"
    CAREGIVER_REPORTED = "CAREGIVER-REPORTED"
    PATIENT_REPORTED = "PATIENT-REPORTED"
    MEDICAL_RECORD = "MEDICAL-RECORD"
    LAB = "LAB"
    MEDICATION = "MEDICATION"
    AI_DERIVED = "AI-DERIVED"


class EvidenceReference(BaseModel):
    evidence_id: str = Field(..., description="Unique evidence code e.g. EV-CG-045")
    source_type: str = Field(..., description="Source classification e.g. CAREGIVER-REPORTED, CLINICIAN-CONFIRMED")
    observed_at: str = Field(..., description="Date or timestamp of observation")
    original_statement: str = Field(..., description="Verbatim raw record statement")


class ClinicalConsideration(BaseModel):
    title: str = Field(..., description="Clinical consideration title e.g. Orthostatic / Postural Instability Process")
    category: str = Field(..., description="Domain category e.g. Mobility / Hemodynamic / Neurological")
    description: str = Field(..., description="Concise explanation of the potential clinical mechanism")
    status: ConsiderationStatus = Field(
        default=ConsiderationStatus.POSSIBLE_CONSIDERATION,
        description="Default status MUST be POSSIBLE_CONSIDERATION, never DIAGNOSIS"
    )
    supporting_evidence: List[EvidenceReference] = Field(
        default_factory=list,
        description="Documented evidence references supporting this consideration"
    )
    contradicting_evidence: List[str] = Field(
        default_factory=list,
        description="Weakening or contradicting points, or statement that none were identified"
    )
    missing_information: List[str] = Field(
        default_factory=list,
        description="Specific missing clinical parameters needed to evaluate this consideration"
    )
    evidence_strength: EvidenceStrength = Field(
        default=EvidenceStrength.LIMITED,
        description="Controlled strength reflecting actual available evidence"
    )
    reasoning: str = Field(..., description="Clinical rationale connecting observations without asserting diagnosis")
    uncertainty: str = Field(..., description="Explicit description of evidentiary limitations and unknowns")
    references: List[str] = Field(
        default_factory=list,
        description="List of raw evidence IDs referenced (e.g. ['EV-CG-045', 'EV-CG-046'])"
    )


class ClinicalReasoningRequest(BaseModel):
    question: str = Field(..., min_length=3, description="Doctor clinical question")
    doctor_id: Optional[str] = Field("DEMO_DOCTOR", description="Doctor identifier or demo session ID")


class PatientContextSummary(BaseModel):
    patient_id: str
    name: str
    age: int
    sex: str
    diagnoses: List[str]
    active_medications: List[str]
    relevant_observations: List[str]
    relevant_changes: List[str]
    relevant_labs: List[str]
    known_unknowns: List[str]
    conflicts: List[str]
    total_evidence_count: int


class ClinicalReasoningResponse(BaseModel):
    question: str
    patient_id: str
    generated_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    context_summary: PatientContextSummary
    considerations: List[ClinicalConsideration]
    missing_information: List[str]
    red_flags: List[str]
    relevant_changes: List[str]
    limitations: List[str]
    disclaimer: str = (
        "AI-generated clinical reasoning support derived from recorded evidence. "
        "This tool does not establish a medical diagnosis, prescribe treatment, or replace clinical judgment. "
        "The treating clinician remains the sole decision-maker."
    )
    session_id: Optional[str] = None
    model_used: Optional[str] = "claude-3-5-sonnet-20241022 (simulated/mock-compatible)"
    validation_status: str = "PASSED"
