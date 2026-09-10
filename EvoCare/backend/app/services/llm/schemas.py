from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ObservationCategory(str, Enum):
    MOBILITY = "mobility"
    FALL = "fall"
    NEAR_FALL = "near_fall"
    DIZZINESS = "dizziness"
    NUTRITION = "nutrition"
    COGNITION = "cognition"
    SLEEP = "sleep"
    PAIN = "pain"
    BEHAVIOR = "behavior"
    MEDICATION_ADHERENCE = "medication_adherence"
    ACTIVITY = "activity"
    OTHER = "other"

class EventType(str, Enum):
    FALL = "FALL"
    NO_FALL = "NO_FALL"
    NEAR_FALL = "NEAR_FALL"
    DIZZINESS_EPISODE = "DIZZINESS_EPISODE"
    PAIN_REPORT = "PAIN_REPORT"
    APPETITE_CHANGE = "APPETITE_CHANGE"
    CONFUSION_EPISODE = "CONFUSION_EPISODE"
    MEDICATION_EVENT = "MEDICATION_EVENT"
    SLEEP_DISTURBANCE = "SLEEP_DISTURBANCE"
    MOBILITY_ASSIST = "MOBILITY_ASSIST"
    BEHAVIOR_OBSERVATION = "BEHAVIOR_OBSERVATION"
    GENERAL_OBSERVATION = "GENERAL_OBSERVATION"

class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    UNCERTAIN = "UNCERTAIN"

class CertaintyState(str, Enum):
    CONFIRMED = "CONFIRMED"
    UNCERTAIN = "UNCERTAIN"
    SUSPECTED = "SUSPECTED"
    DENIED = "DENIED"

class InformationState(str, Enum):
    OBSERVED = "OBSERVED"
    UNKNOWN = "UNKNOWN"
    NOT_STATED = "NOT_STATED"

class ProcessingMode(str, Enum):
    AUTO = "AUTO"
    DETERMINISTIC = "DETERMINISTIC"
    LLM = "LLM"

class ProcessingMethod(str, Enum):
    DETERMINISTIC = "DETERMINISTIC"
    LLM_ASSISTED = "LLM_ASSISTED"
    LLM_FALLBACK = "LLM_FALLBACK"

class LLMStatus(str, Enum):
    SUCCESS = "SUCCESS"
    LLM_UNAVAILABLE = "LLM_UNAVAILABLE"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    SAFETY_REJECTED = "SAFETY_REJECTED"
    ERROR = "ERROR"

class ParsedCaregiverObservation(BaseModel):
    category: ObservationCategory = Field(..., description="The primary functional or clinical observation domain category")
    subject: str = Field(default="patient", description="Subject of the observation")
    event_type: Optional[str] = Field(default=None, description="Granular event type classification (e.g. NEAR_FALL, FALL, NO_FALL)")
    severity: str = Field(default="UNKNOWN", description="Explicitly stated severity (e.g., Mild, Moderate, Severe, or UNKNOWN)")
    duration: str = Field(default="UNKNOWN", description="Explicitly stated duration (e.g., 5 minutes, 10 minutes, or UNKNOWN)")
    frequency: str = Field(default="UNKNOWN", description="Explicitly stated frequency (e.g., once, 3 times, daily, or UNKNOWN)")
    onset: str = Field(default="UNKNOWN", description="Explicitly stated temporal onset or trigger (e.g., after standing up, yesterday, or UNKNOWN)")
    context: str = Field(default="UNKNOWN", description="Contextual location or setting (e.g., bedroom, bathroom, morning, or UNKNOWN)")
    functional_impact: str = Field(default="UNKNOWN", description="Impact on functional activities or walking support required")
    associated_details: Dict[str, Any] = Field(default_factory=dict, description="Additional explicit domain details (e.g., meal name, amount eaten)")
    negations: List[str] = Field(default_factory=list, description="Explicitly negated events (e.g., 'did not fall', 'no injury')")
    confidence: ConfidenceLevel = Field(default=ConfidenceLevel.HIGH, description="Linguistic confidence of the statement (e.g. LOW/UNCERTAIN for 'I think')")
    certainty: CertaintyState = Field(default=CertaintyState.CONFIRMED, description="Certainty state of the caregiver statement")
    unknown_fields: List[str] = Field(default_factory=list, description="List of relevant category fields not stated in the input")
    requires_clarification: bool = Field(default=False, description="Whether essential category fields are missing and require clarification")
    clarification_fields: List[str] = Field(default_factory=list, description="Ordered list of missing fields requiring clarification")
    
    # Safety invariant fields
    etiology: str = Field(default="UNKNOWN", description="MUST be UNKNOWN. Never infer clinical causes or diagnoses")
    diagnosis: Optional[str] = Field(default=None, description="MUST be None. LLM cannot diagnose diseases")
    dementia_diagnosed: bool = Field(default=False, description="MUST be False. Confusion is never converted into dementia")
    clinical_diagnoses_inferred: bool = Field(default=False, description="MUST be False. Flag verifying no clinical diagnoses inferred")
    ground_impact: Optional[bool] = Field(default=None, description="Whether impact occurred (False for near-falls, True for completed falls)")
    raw_statement: Optional[str] = Field(default=None, description="The original raw input string from caregiver")

    model_config = ConfigDict(extra="ignore")
