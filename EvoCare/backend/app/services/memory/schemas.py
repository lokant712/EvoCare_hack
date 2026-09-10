from enum import Enum
from datetime import datetime
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict

class MemoryUpdateType(str, Enum):
    NEW_CLAIM = "NEW_CLAIM"
    CONFIRM_CLAIM = "CONFIRM_CLAIM"
    TEMPORAL_UPDATE = "TEMPORAL_UPDATE"
    CONFLICT = "CONFLICT"
    OUTDATED = "OUTDATED"
    NO_CHANGE = "NO_CHANGE"

class InformationStateEnum(str, Enum):
    OBSERVED = "OBSERVED"
    CLINICIAN_CONFIRMED = "CLINICIAN_CONFIRMED"
    AI_DERIVED = "AI_DERIVED"
    HISTORICAL = "HISTORICAL"
    OUTDATED = "OUTDATED"
    CONFLICTING = "CONFLICTING"
    UNKNOWN = "UNKNOWN"

class ProposalStatusEnum(str, Enum):
    CREATED = "CREATED"
    VALIDATED = "VALIDATED"
    REJECTED = "REJECTED"
    APPLIED = "APPLIED"

class MemoryConsolidateRequest(BaseModel):
    patient_id: Optional[str] = "P001"
    evidence_id: Optional[str] = None  # e.g. "EV-CG-021" or database id as string
    evidence_code: Optional[str] = None

class MemoryProposalResponse(BaseModel):
    proposal_id: int
    proposal_code: str
    patient_id: int
    patient_code: str
    memory_page: str
    category: str
    update_type: str
    proposed_claim: str
    information_state: str
    evidence_ids: List[str]
    confidence: str
    status: str
    validation_errors: List[str] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class MemoryApplyResponse(BaseModel):
    status: str
    memory_version_id: int
    version: int
    memory_page: str
    wiki_page: str
    applied_claim: str
    evidence_ids: List[str]
    applied_at: datetime

class MemoryClaimResponse(BaseModel):
    id: int
    claim_code: str
    patient_id: int
    memory_page: str
    category: str
    statement: str
    information_state: str
    source_types: List[str]
    evidence_ids: List[str]
    confidence: str
    first_observed_at: datetime
    last_observed_at: datetime
    version: int
    active: bool

    model_config = ConfigDict(from_attributes=True)

class MemoryVersionResponse(BaseModel):
    id: int
    patient_id: int
    memory_page: str
    version_number: int
    previous_version_id: Optional[int] = None
    update_type: str
    change_summary: str
    created_at: datetime
    created_by: str
    validation_status: str

    model_config = ConfigDict(from_attributes=True)

class MemoryDiffResponse(BaseModel):
    patient_id: int
    memory_page: str
    current_version: int
    previous_version: Optional[int] = None
    added_claims: List[str] = []
    preserved_claims: List[str] = []
    evidence_ids: List[str] = []
    raw_diff: str = ""
