import re
import logging
from typing import Tuple, List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.memory_models import MemoryProposal

logger = logging.getLogger(__name__)

PROHIBITED_MEMORY_DIAGNOSES = [
    "dementia", "alzheimer", "stroke", "cerebrovascular", "parkinson",
    "hypotension", "orthostatic hypotension", "vertigo", "dehydration",
    "hypoglycemia", "anemia", "infection", "sepsis", "neuropathy"
]

class MemoryValidator:
    @classmethod
    def validate_proposal(
        cls,
        db: Session,
        patient_id: int,
        evidence: Evidence,
        proposal_dict: Dict[str, Any]
    ) -> Tuple[bool, List[str]]:
        """
        Deterministically validates a Memory Proposal.
        Returns (is_valid, list_of_errors).
        """
        errors: List[str] = []

        # 1. Verify Patient Existence
        patient = db.query(Patient).filter(Patient.id == patient_id).first()
        if not patient:
            errors.append(f"Patient ID {patient_id} does not exist.")
            return False, errors

        # 2. Strict Patient Isolation Check
        if evidence.patient_id != patient_id:
            errors.append(f"PATIENT ISOLATION VIOLATION: Evidence {evidence.evidence_code} belongs to Patient {evidence.patient_id}, not {patient_id}.")
            return False, errors

        # 3. Mandatory Provenance / Evidence Codes
        evidence_ids = proposal_dict.get("evidence_ids", [])
        if not evidence_ids or not isinstance(evidence_ids, list):
            errors.append("PROVENANCE ERROR: Proposed memory claim must include at least one supporting Evidence ID.")
        else:
            for ev_code in evidence_ids:
                matching_ev = db.query(Evidence).filter(
                    Evidence.evidence_code == ev_code,
                    Evidence.patient_id == patient_id
                ).first()
                if not matching_ev:
                    errors.append(f"PROVENANCE ERROR: Cited evidence {ev_code} does not exist for Patient {patient_id}.")

        # 4. Check Claim Content & Prohibited Diagnoses
        claim_text = proposal_dict.get("proposed_claim", "")
        if not claim_text or len(claim_text.strip()) < 5:
            if proposal_dict.get("update_type") != "NO_CHANGE":
                errors.append("Proposed claim statement cannot be empty.")

        claim_lower = claim_text.lower()
        for prog in PROHIBITED_MEMORY_DIAGNOSES:
            # Check for words like "dementia", "stroke", etc. in proposed claim unless explicitly negated
            if re.search(rf"\b{prog}\b", claim_lower):
                errors.append(f"CLINICAL SAFETY VIOLATION: Proposed memory claim introduces unconfirmed clinical diagnosis/etiology '{prog}'.")

        # 5. Near-Fall Invariant
        ev_statement_lower = evidence.original_statement.lower()
        if "almost fell" in ev_statement_lower or "nearly fell" in ev_statement_lower:
            if re.search(r"\b(patient fell|had a fall|completed fall|fell down)\b", claim_lower):
                errors.append("SAFETY VIOLATION: Near-fall observation cannot be upgraded into a completed FALL.")

        # 6. Medical Record Separation (Cannot modify clinical/medication records)
        if any(term in claim_lower for term in ["prescribed", "medication discontinued", "lab normal value modified", "physician diagnosis updated"]):
            errors.append("RECORD SEPARATION VIOLATION: Memory updates cannot alter authoritative clinician or laboratory records.")

        is_valid = len(errors) == 0
        if not is_valid:
            logger.warning(f"Memory proposal rejected for patient {patient_id}: {errors}")

        return is_valid, errors
