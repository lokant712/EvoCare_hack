import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.baseline import Baseline
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.conflict import Conflict
from app.models.memory_models import MemoryClaim, MemoryVersion

logger = logging.getLogger(__name__)

CATEGORY_TO_PAGE_MAP = {
    "mobility": "Mobility",
    "fall": "Falls",
    "near_fall": "Falls",
    "dizziness": "Dizziness",
    "cognition": "Cognition",
    "nutrition": "Nutrition",
    "sleep": "Sleep",
    "pain": "Pain",
    "behavior": "Behavior",
    "medication_adherence": "Medication Adherence",
    "activity": "Mobility",
    "other": "Patient Overview"
}

class MemoryRetriever:
    @staticmethod
    def map_category_to_page(category: str) -> str:
        cat_clean = category.lower().replace(" ", "_") if category else "other"
        return CATEGORY_TO_PAGE_MAP.get(cat_clean, "Mobility")

    @classmethod
    def retrieve_context_for_evidence(
        cls,
        db: Session,
        patient_id: int,
        evidence: Evidence
    ) -> Dict[str, Any]:
        """
        Retrieves relevant historical memory, baseline, related observations, and active claims.
        Enforces strict patient isolation: evidence.patient_id MUST equal patient_id.
        """
        # Hard Rule: Patient Isolation
        if evidence.patient_id != patient_id:
            logger.error(f"PATIENT ISOLATION VIOLATION: Evidence {evidence.evidence_code} (Patient {evidence.patient_id}) does not match requested Patient {patient_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Patient isolation violation: Evidence {evidence.evidence_code} belongs to patient {evidence.patient_id}, not {patient_id}."
            )

        # 1. Determine Category & Page
        category = "mobility"
        # Check if linked to caregiver observation
        cg_obs = db.query(CaregiverObservation).filter(CaregiverObservation.evidence_id == evidence.id).first()
        if cg_obs:
            category = cg_obs.category
        elif "fall" in evidence.original_statement.lower():
            category = "fall"
        elif "dizzy" in evidence.original_statement.lower():
            category = "dizziness"
        elif "confus" in evidence.original_statement.lower():
            category = "cognition"
        elif "eat" in evidence.original_statement.lower() or "dinner" in evidence.original_statement.lower():
            category = "nutrition"
        elif "sleep" in evidence.original_statement.lower():
            category = "sleep"
        elif "pain" in evidence.original_statement.lower() or "hurt" in evidence.original_statement.lower():
            category = "pain"

        memory_page = cls.map_category_to_page(category)

        # 2. Retrieve Baseline
        baseline = db.query(Baseline).filter(
            Baseline.patient_id == patient_id,
            Baseline.category.ilike(f"%{category}%")
        ).first()
        baseline_statement = baseline.baseline_value if baseline else "Historically independently functional without assistive aids."


        # 3. Retrieve Historical Clinical Doctor Records
        doctor_records = db.query(DoctorRecord).filter(
            DoctorRecord.patient_id == patient_id
        ).all()
        doc_summaries = [
            f"{d.doctor_id} ({d.record_type}) on {d.observed_at.strftime('%Y-%m-%d')}: {d.content}"
            for d in doctor_records if category in d.content.lower() or "independent" in d.content.lower()
        ]


        # 4. Retrieve Recent Observations (Same or closely related categories)
        related_cats = [category]
        if category in ("mobility", "fall", "near_fall"):
            related_cats = ["mobility", "fall", "near_fall", "dizziness"]

        recent_obs = db.query(CaregiverObservation).filter(
            CaregiverObservation.patient_id == patient_id,
            CaregiverObservation.category.in_(related_cats)
        ).order_by(CaregiverObservation.observed_at.desc()).limit(8).all()

        recent_obs_data = [
            {
                "date": o.observed_at.strftime("%Y-%m-%d"),
                "caregiver_id": o.caregiver_id,
                "statement": o.observation_text,
                "category": o.category,
                "attributes": o.attributes,
                "evidence_code": o.evidence.evidence_code if o.evidence else "UNKNOWN"
            }
            for o in recent_obs
        ]

        # 5. Retrieve Active Memory Claims
        active_claims = db.query(MemoryClaim).filter(
            MemoryClaim.patient_id == patient_id,
            MemoryClaim.memory_page == memory_page,
            MemoryClaim.active == True
        ).all()
        claims_data = [
            {
                "claim_code": c.claim_code,
                "statement": c.statement,
                "information_state": c.information_state,
                "evidence_ids": c.evidence_ids,
                "version": c.version
            }
            for c in active_claims
        ]

        # 6. Retrieve Latest Memory Version
        latest_version = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == patient_id,
            MemoryVersion.memory_page == memory_page
        ).order_by(MemoryVersion.version_number.desc()).first()

        current_version_num = latest_version.version_number if latest_version else 1

        # 7. Retrieve Relevant Conflicts
        conflicts = db.query(Conflict).filter(
            Conflict.patient_id == patient_id
        ).all()
        conflict_summaries = [
            f"{c.title}: {c.description}"
            for c in conflicts if category in c.title.lower() or category in c.description.lower()
        ]

        return {
            "patient_id": patient_id,
            "evidence": {
                "id": evidence.id,
                "evidence_code": evidence.evidence_code,
                "source_type": evidence.source_type.value,
                "source_id": evidence.source_id,
                "original_statement": evidence.original_statement,
                "observed_at": evidence.observed_at.strftime("%Y-%m-%d %H:%M:%S")
            },
            "category": category,
            "memory_page": memory_page,
            "baseline": baseline_statement,
            "clinical_documentation": doc_summaries,
            "recent_observations": recent_obs_data,
            "active_claims": claims_data,
            "current_version_number": current_version_num,
            "conflicts": conflict_summaries
        }
