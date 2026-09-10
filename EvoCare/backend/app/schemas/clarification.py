from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.clarification import SessionStatus

class ObservationStartRequest(BaseModel):
    patient_id: Optional[str] = "P001"
    patient_code: Optional[str] = None
    text: str
    caregiver_id: Optional[str] = "CG001"
    processing_mode: Optional[str] = "AUTO"  # AUTO | DETERMINISTIC | LLM

class ClarificationQuestionResponse(BaseModel):
    id: int
    field_name: str
    question: str
    required: bool
    options: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class ObservationStartResponse(BaseModel):
    session_id: int
    session_code: str
    patient_id: int
    patient_code: str
    category: str
    missing_fields: List[str]
    questions: List[ClarificationQuestionResponse]
    status: Any
    processing_method: Optional[str] = "DETERMINISTIC"
    next_question: Optional[ClarificationQuestionResponse] = None
    observation: Optional[Dict[str, Any]] = None


class ClarificationAnswerRequest(BaseModel):
    question_id: Optional[int] = None
    field_name: Optional[str] = None
    answer: str

class ClarificationAnswerResponse(BaseModel):
    id: int
    session_id: int
    field_name: str
    answer: str
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClarificationSessionResponse(BaseModel):
    id: int
    session_code: str
    patient_id: int
    patient_code: str
    raw_text: str
    detected_category: str
    status: SessionStatus
    questions: List[ClarificationQuestionResponse]
    answers: List[ClarificationAnswerResponse]
    started_at: datetime
    completed_at: Optional[datetime] = None

class ObservationCompleteResponse(BaseModel):
    session_id: int
    status: SessionStatus
    category: str
    structured_observation: Dict[str, Any]
    evidence_id: int
    evidence_code: str
    observation_id: int
    created_at: datetime
    wiki_updated: Optional[bool] = False
    wiki_files: Optional[List[str]] = None

class StructuredObservationDetailResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    source_type: str = "CAREGIVER"
    category: str
    observation_text: str
    attributes: Optional[Dict[str, Any]] = None
    observed_at: datetime
    information_state: str
    clarification_completed: bool
