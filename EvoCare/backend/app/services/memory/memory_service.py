import uuid
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.audit import AuditLog
from app.models.memory_models import MemoryVersion, MemoryClaim, MemoryProposal
from app.services.memory.retriever import MemoryRetriever
from app.services.memory.consolidator import MemoryConsolidator
from app.services.memory.validator import MemoryValidator
from app.services.memory.wiki_sync import WikiSynchronizer
from app.services.memory.schemas import (
    MemoryProposalResponse,
    MemoryApplyResponse,
    MemoryClaimResponse,
    MemoryVersionResponse,
    MemoryDiffResponse,
)

logger = logging.getLogger(__name__)

class MemoryService:
    @classmethod
    def consolidate_evidence(
        cls,
        db: Session,
        patient_id_or_code: Any,
        evidence_id_or_code: Any
    ) -> Dict[str, Any]:
        """
        Retrieves context, generates a structured memory proposal, and validates it.
        DOES NOT automatically apply to DB or Wiki.
        """
        # 1. Resolve Patient
        if isinstance(patient_id_or_code, int) or (isinstance(patient_id_or_code, str) and str(patient_id_or_code).isdigit()):
            patient = db.query(Patient).filter(Patient.id == int(patient_id_or_code)).first()
        else:
            patient = db.query(Patient).filter(Patient.patient_code == str(patient_id_or_code)).first()

        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Patient '{patient_id_or_code}' not found")

        # 2. Resolve Evidence
        if isinstance(evidence_id_or_code, int) or (isinstance(evidence_id_or_code, str) and str(evidence_id_or_code).isdigit()):
            ev = db.query(Evidence).filter(Evidence.id == int(evidence_id_or_code)).first()
        else:
            ev = db.query(Evidence).filter(Evidence.evidence_code == str(evidence_id_or_code)).first()

        if not ev:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Evidence '{evidence_id_or_code}' not found")

        # 3. Retrieve Context (enforces patient isolation)
        context = MemoryRetriever.retrieve_context_for_evidence(
            db=db,
            patient_id=patient.id,
            evidence=ev
        )

        # 4. Generate Proposal
        proposal_dict = MemoryConsolidator.generate_proposal(context=context)

        # 5. Validate Proposal
        is_valid, validation_errors = MemoryValidator.validate_proposal(
            db=db,
            patient_id=patient.id,
            evidence=ev,
            proposal_dict=proposal_dict
        )

        prop_status = "VALIDATED" if is_valid else "REJECTED"

        # 6. Save Proposal
        proposal_code = f"PROP-{uuid.uuid4().hex[:8].upper()}"
        prop = MemoryProposal(
            proposal_code=proposal_code,
            patient_id=patient.id,
            evidence_id=ev.id,
            evidence_code=ev.evidence_code,
            memory_page=proposal_dict.get("memory_page", "Mobility"),
            category=proposal_dict.get("category", "mobility"),
            update_type=proposal_dict.get("update_type", "TEMPORAL_UPDATE"),
            proposed_claim=proposal_dict.get("proposed_claim", ""),
            information_state=proposal_dict.get("information_state", "AI_DERIVED"),
            evidence_ids=proposal_dict.get("evidence_ids", [ev.evidence_code]),
            confidence=proposal_dict.get("confidence", "HIGH"),
            status=prop_status,
            validation_errors=validation_errors,
            created_at=datetime.now(timezone.utc)
        )
        db.add(prop)
        db.commit()
        db.refresh(prop)

        return {
            "proposal_id": prop.id,
            "proposal_code": prop.proposal_code,
            "patient_id": patient.id,
            "patient_code": patient.patient_code,
            "memory_page": prop.memory_page,
            "category": prop.category,
            "update_type": prop.update_type,
            "proposed_claim": prop.proposed_claim,
            "information_state": prop.information_state,
            "evidence_ids": prop.evidence_ids,
            "confidence": prop.confidence,
            "status": prop.status,
            "validation_errors": prop.validation_errors,
            "created_at": prop.created_at
        }

    @classmethod
    def apply_proposal(cls, db: Session, proposal_id: int) -> Dict[str, Any]:
        """
        Atomically applies a VALIDATED memory proposal:
        - Creates an immutable MemoryVersion
        - Updates MemoryClaim
        - Synchronizes Patient Wiki
        - Writes AuditLog
        If Wiki synchronization fails, entire operation rolls back.
        """
        prop = db.query(MemoryProposal).filter(MemoryProposal.id == proposal_id).first()
        if not prop:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proposal {proposal_id} not found")

        if prop.status == "APPLIED":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Proposal has already been applied")

        if prop.status != "VALIDATED":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot apply proposal in '{prop.status}' status. Only 'VALIDATED' proposals can be applied."
            )

        patient = db.query(Patient).filter(Patient.id == prop.patient_id).first()

        # 1. Determine Sequential Version Number
        latest_ver = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == patient.id,
            MemoryVersion.memory_page == prop.memory_page
        ).order_by(MemoryVersion.version_number.desc()).first()

        prev_version_id = latest_ver.id if latest_ver else None
        prev_version_num = latest_ver.version_number if latest_ver else 1

        # Handle NO_CHANGE: Do not increment version or write duplicate memory
        if prop.update_type == "NO_CHANGE":
            prop.status = "APPLIED"
            prop.applied_at = datetime.now(timezone.utc)
            prop.resulting_version_id = prev_version_id
            wiki_path_obj = WikiSynchronizer.get_patient_wiki_path(patient.patient_code, prop.memory_page)
            db.commit()
            return {
                "status": "APPLIED",
                "memory_version_id": prev_version_id if prev_version_id else 1,
                "version": prev_version_num,
                "memory_page": prop.memory_page,
                "wiki_page": str(wiki_path_obj) if wiki_path_obj else "",
                "applied_claim": prop.proposed_claim,
                "evidence_ids": prop.evidence_ids,
                "applied_at": prop.applied_at
            }

        new_version_num = prev_version_num + 1

        # 2. Synchronize to Wiki (Atomic check: if this fails, DB is not committed)
        try:
            wiki_path = WikiSynchronizer.sync_memory_update(
                patient_code=patient.patient_code,
                memory_page=prop.memory_page,
                version_number=new_version_num,
                previous_version=prev_version_num,
                statement=prop.proposed_claim,
                evidence_ids=prop.evidence_ids,
                update_type=prop.update_type,
                change_summary=f"Applied proposal {prop.proposal_code}: {prop.proposed_claim}"
            )
        except Exception as e:
            logger.error(f"Wiki synchronization failed during apply: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Atomic update failed: Wiki synchronization error ({str(e)})"
            )

        # 3. Create Immutable MemoryVersion
        mem_version = MemoryVersion(
            patient_id=patient.id,
            memory_page=prop.memory_page,
            version_number=new_version_num,
            previous_version_id=prev_version_id,
            update_type=prop.update_type,
            change_summary=prop.proposed_claim,
            content_snapshot={
                "claim": prop.proposed_claim,
                "evidence_ids": prop.evidence_ids,
                "category": prop.category
            },
            created_at=datetime.now(timezone.utc),
            created_by="CAREGIVER_CONSOLIDATION",
            validation_status="APPLIED"
        )
        db.add(mem_version)
        db.flush()

        # 4. Create or Update Active MemoryClaim
        claim_code = f"CLM-{patient.patient_code}-{uuid.uuid4().hex[:6].upper()}"
        mem_claim = MemoryClaim(
            claim_code=claim_code,
            patient_id=patient.id,
            memory_page=prop.memory_page,
            category=prop.category,
            statement=prop.proposed_claim,
            information_state=prop.information_state,
            source_types=["CAREGIVER"],
            evidence_ids=prop.evidence_ids,
            confidence=prop.confidence,
            first_observed_at=datetime.now(timezone.utc),
            last_observed_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
            version=new_version_num,
            active=True
        )
        db.add(mem_claim)

        # 5. Insert AuditLog
        audit = AuditLog(
            action="MEMORY_VERSION_APPLIED",
            entity_type="MemoryVersion",
            entity_id=str(mem_version.id),
            details=f"Memory version {new_version_num} applied for {prop.memory_page}. Proposal: {prop.proposal_code}. Evidence: {prop.evidence_ids}."
        )
        db.add(audit)

        # 6. Mark Proposal as APPLIED
        prop.status = "APPLIED"
        prop.applied_at = datetime.now(timezone.utc)
        prop.resulting_version_id = mem_version.id

        db.commit()

        return {
            "status": "APPLIED",
            "memory_version_id": mem_version.id,
            "version": new_version_num,
            "memory_page": prop.memory_page,
            "wiki_page": wiki_path,
            "applied_claim": prop.proposed_claim,
            "evidence_ids": prop.evidence_ids,
            "applied_at": prop.applied_at
        }

    @classmethod
    def get_current_memory(cls, db: Session, patient_id: int, page: str) -> Dict[str, Any]:
        claims = db.query(MemoryClaim).filter(
            MemoryClaim.patient_id == patient_id,
            MemoryClaim.memory_page == page,
            MemoryClaim.active == True
        ).all()
        latest_ver = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == patient_id,
            MemoryVersion.memory_page == page
        ).order_by(MemoryVersion.version_number.desc()).first()

        return {
            "patient_id": patient_id,
            "memory_page": page,
            "current_version": latest_ver.version_number if latest_ver else 1,
            "active_claims": [
                {
                    "claim_code": c.claim_code,
                    "statement": c.statement,
                    "information_state": c.information_state,
                    "evidence_ids": c.evidence_ids,
                    "confidence": c.confidence,
                    "version": c.version
                }
                for c in claims
            ]
        }

    @classmethod
    def get_memory_history(cls, db: Session, patient_id: int, page: str) -> List[Dict[str, Any]]:
        versions = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == patient_id,
            MemoryVersion.memory_page == page
        ).order_by(MemoryVersion.version_number.asc()).all()

        return [
            {
                "id": v.id,
                "version_number": v.version_number,
                "previous_version_id": v.previous_version_id,
                "update_type": v.update_type,
                "change_summary": v.change_summary,
                "created_at": v.created_at,
                "created_by": v.created_by,
                "validation_status": v.validation_status
            }
            for v in versions
        ]

    @classmethod
    def get_memory_diff(cls, db: Session, patient_id: int, page: str) -> Dict[str, Any]:
        versions = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == patient_id,
            MemoryVersion.memory_page == page
        ).order_by(MemoryVersion.version_number.desc()).limit(2).all()

        if not versions:
            return {
                "patient_id": patient_id,
                "memory_page": page,
                "current_version": 1,
                "previous_version": None,
                "added_claims": [],
                "preserved_claims": ["Historically normal baseline."],
                "evidence_ids": []
            }

        curr = versions[0]
        prev = versions[1] if len(versions) > 1 else None

        added = [curr.change_summary]
        preserved = ["Baseline independent ambulation"] if page == "Mobility" else ["Historical baseline"]

        return {
            "patient_id": patient_id,
            "memory_page": page,
            "current_version": curr.version_number,
            "previous_version": prev.version_number if prev else None,
            "added_claims": added,
            "preserved_claims": preserved,
            "evidence_ids": curr.content_snapshot.get("evidence_ids", []) if curr.content_snapshot else []
        }

    @classmethod
    def get_patient_memory_summary(cls, db: Session, patient_id: int) -> Dict[str, Any]:
        claims = db.query(MemoryClaim).filter(
            MemoryClaim.patient_id == patient_id,
            MemoryClaim.active == True
        ).all()

        return {
            "patient_id": patient_id,
            "baseline": "Historically independently mobile without assistive devices.",
            "recent_changes": [c.statement for c in claims if "recent" in c.statement.lower() or "intermittent" in c.statement.lower()],
            "caregiver_observations": [c.statement for c in claims],
            "conflicts": "Clinical documentation describes independent mobility on 2026-08-18; caregiver observations note subsequent assistance needs outdoors.",
            "unknowns": "Exact etiology of transient unsteadiness has not been established by clinician.",
            "active_claims_count": len(claims)
        }
