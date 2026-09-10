from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.observation import Observation
from app.models.evidence import Evidence
from app.schemas.pattern import PatternProvenanceResponse
from app.schemas.conflict import ConflictProvenanceResponse
from app.schemas.evidence import EvidenceResponse

class ProvenanceService:
    @staticmethod
    def get_pattern_provenance(db: Session, pattern_id: int) -> PatternProvenanceResponse:
        pattern = db.query(Pattern).filter(Pattern.id == pattern_id).first()
        if not pattern:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern with id {pattern_id} not found"
            )
        
        supporting = [EvidenceResponse.model_validate(ev) for ev in pattern.supporting_evidences]
        return PatternProvenanceResponse(
            pattern_id=pattern.id,
            title=pattern.title,
            category=pattern.category,
            description=pattern.description,
            status=pattern.status,
            detected_at=pattern.detected_at,
            supporting_evidence=supporting
        )

    @staticmethod
    def get_conflict_provenance(db: Session, conflict_id: int) -> ConflictProvenanceResponse:
        conflict = db.query(Conflict).filter(Conflict.id == conflict_id).first()
        if not conflict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conflict with id {conflict_id} not found"
            )
        
        supporting = [EvidenceResponse.model_validate(ev) for ev in conflict.supporting_evidences]
        return ConflictProvenanceResponse(
            conflict_id=conflict.id,
            title=conflict.title,
            category=conflict.category,
            description=conflict.description,
            doctor_view=conflict.doctor_view,
            caregiver_view=conflict.caregiver_view,
            status=conflict.status,
            supporting_evidence=supporting
        )

    @staticmethod
    def get_observation_provenance(db: Session, observation_id: int) -> EvidenceResponse:
        observation = db.query(Observation).filter(Observation.id == observation_id).first()
        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Observation with id {observation_id} not found"
            )
        return EvidenceResponse.model_validate(observation.evidence)
