import os
import uuid
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.core.database import utc_now
from app.models.patient import Patient
from app.models.security import User
from app.models.evidence import Evidence
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.enums import SourceType, EvidenceStatus
from app.services.audit_service import AuditService
from app.schemas.doctor_entry import (
    DoctorEntryBatchRequest,
    DoctorEntryBatchResponse,
    DiagnosisEntryItem,
    PrescriptionEntryItem
)

logger = logging.getLogger(__name__)


class DoctorEntryService:
    @classmethod
    def record_clinical_entries(
        cls,
        db: Session,
        patient: Patient,
        doctor: User,
        data: DoctorEntryBatchRequest,
        ip_address: str = "127.0.0.1"
    ) -> DoctorEntryBatchResponse:
        """
        Persists doctor diagnoses and prescriptions into structured tables,
        generates immutable Evidence entries, converts the structured tables
        into a clean Markdown (.md) document, and writes it to the knowledge base.
        """
        now = datetime.now(timezone.utc)
        now_str = now.strftime("%Y-%m-%d %H:%M:%S UTC")
        date_slug = now.strftime("%Y%m%d")
        ts_slug = now.strftime("%H%M%S")
        evidence_codes_generated: List[str] = []

        def get_unique_evidence_code(prefix: str) -> str:
            count = db.query(Evidence).filter(Evidence.evidence_code.like(f"{prefix}-%")).count() + 1
            candidate = f"{prefix}-{count:03d}"
            while db.query(Evidence).filter(Evidence.evidence_code == candidate).first() is not None:
                count += 1
                candidate = f"{prefix}-{count:03d}"
            return candidate

        # 1. Process Diagnoses
        diagnosis_rows: List[Tuple[DiagnosisEntryItem, str]] = []
        for diag in data.diagnoses:
            ev_code = get_unique_evidence_code(f"EV-DR-{patient.patient_code}")
            evidence_codes_generated.append(ev_code)

            # Create immutable Evidence row
            statement = f"Clinical Diagnosis: {diag.condition} ({diag.icd_code or 'ICD: Unspecified'}). Status: {diag.status}. Notes: {diag.notes or 'No additional notes'}"
            ev = Evidence(
                patient_id=patient.id,
                evidence_code=ev_code,
                source_type=SourceType.DOCTOR,
                source_id=doctor.username,
                observed_at=now.replace(tzinfo=None),
                recorded_at=now.replace(tzinfo=None),
                original_statement=statement,
                status=EvidenceStatus.IMMUTABLE,
                created_at=utc_now()
            )
            db.add(ev)
            db.flush()

            # Create DoctorRecord row
            content_desc = f"Diagnosis: {diag.condition} [{diag.icd_code or 'N/A'}]. Status: {diag.status}. Clinical Rationale: {diag.notes or 'None'}"
            dr_rec = DoctorRecord(
                patient_id=patient.id,
                evidence_id=ev.id,
                doctor_id=doctor.username,
                record_type="diagnosis",
                content=content_desc,
                observed_at=now.replace(tzinfo=None),
                created_at=utc_now()
            )
            db.add(dr_rec)
            diagnosis_rows.append((diag, ev_code))

        # 2. Process Prescriptions
        prescription_rows: List[Tuple[PrescriptionEntryItem, str]] = []
        for med in data.prescriptions:
            ev_code = get_unique_evidence_code(f"EV-MED-{patient.patient_code}")
            evidence_codes_generated.append(ev_code)

            # Create immutable Evidence row
            statement = f"Doctor Prescription: {med.medication_name} {med.dose}, {med.frequency}. Indication: {med.indication or 'General management'}. Instructions: {med.instructions or 'As directed'}"
            ev = Evidence(
                patient_id=patient.id,
                evidence_code=ev_code,
                source_type=SourceType.DOCTOR,
                source_id=doctor.username,
                observed_at=now.replace(tzinfo=None),
                recorded_at=now.replace(tzinfo=None),
                original_statement=statement,
                status=EvidenceStatus.IMMUTABLE,
                created_at=utc_now()
            )
            db.add(ev)
            db.flush()

            # Create Medication row
            med_rec = Medication(
                patient_id=patient.id,
                evidence_id=ev.id,
                name=med.medication_name,
                dose=med.dose,
                frequency=med.frequency,
                status="ACTIVE",
                indication=med.indication or "Clinician prescribed",
                start_date=now.replace(tzinfo=None),
                created_at=utc_now()
            )
            db.add(med_rec)
            prescription_rows.append((med, ev_code))

        # Commit all database entities
        db.commit()

        # 3. Generate Structured Markdown (.md) File
        md_lines = [
            f"# Doctor Clinical Consultation & Treatment Note",
            f"",
            f"- **Patient**: {patient.name} (`{patient.patient_code}`)",
            f"- **Age / Sex**: {patient.age} years • {patient.sex}",
            f"- **Attending Physician**: {doctor.full_name} (`{doctor.username}`)",
            f"- **Encounter Date**: {now_str}",
            f"- **Encounter Title**: {data.consultation_title or 'Clinical Evaluation'}",
            f"",
            f"---",
            f"",
            f"## Clinical Notes & Summary",
            f"{data.clinical_notes or 'Routine clinical evaluation and longitudinal trajectory review.'}",
            f"",
            f"## Recorded Diagnoses",
            f"| Condition | ICD-10 Code | Status | Clinical Rationale / Notes | Evidence Code |",
            f"| :--- | :--- | :--- | :--- | :--- |"
        ]

        if diagnosis_rows:
            for diag, ev_code in diagnosis_rows:
                icd = diag.icd_code if diag.icd_code else "Unspecified"
                notes = (diag.notes or "—").replace("\n", " ")
                md_lines.append(f"| **{diag.condition}** | `{icd}` | {diag.status} | {notes} | `{ev_code}` |")
        else:
            md_lines.append("| *No new diagnoses entered in this encounter* | — | — | — | — |")

        md_lines.extend([
            f"",
            f"## Prescribed Medications",
            f"| Medication | Dosage | Frequency | Indication | Patient Instructions | Evidence Code |",
            f"| :--- | :--- | :--- | :--- | :--- | :--- |"
        ])

        if prescription_rows:
            for med, ev_code in prescription_rows:
                ind = (med.indication or "—").replace("\n", " ")
                instr = (med.instructions or "As directed").replace("\n", " ")
                md_lines.append(f"| **{med.medication_name}** | {med.dose} | {med.frequency} | {ind} | {instr} | `{ev_code}` |")
        else:
            md_lines.append("| *No new medications prescribed in this encounter* | — | — | — | — | — |")

        md_lines.extend([
            f"",
            f"---",
            f"",
            f"### Provenance & Audit Verification",
            f"- **Total Evidence Entries Generated**: {len(evidence_codes_generated)}",
            f"- **Evidence Invariant**: All records set to `IMMUTABLE` in SQLite evidence store.",
            f"- **Recording Clinician ID**: `{doctor.username}`",
            f"- **System Record ID**: `ENC-{patient.patient_code}-{date_slug}-{ts_slug}`",
            f""
        ])

        markdown_content = "\n".join(md_lines)

        # 4. Save to Knowledge Base Directories
        file_name = f"Consultation_{patient.patient_code}_{date_slug}_{ts_slug}.md"
        saved_file_path = None

        from app.core.config import settings
        kb_root = Path(settings.KNOWLEDGE_BASE_DIR)
        candidate_dirs = [
            kb_root / "Doctor Records"
        ]

        for target_dir in candidate_dirs:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                full_path = target_dir / file_name
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                saved_file_path = str(full_path)
                logger.info(f"Saved doctor consultation markdown note at {full_path}")
            except Exception as e:
                logger.warning(f"Could not write markdown note to {target_dir}: {e}")

        # 5. Log Audit Event
        AuditService.log_audit_event(
            db=db,
            action="DOCTOR_CLINICAL_ENTRY",
            user_id=doctor.id,
            username=doctor.username,
            role="DOCTOR",
            patient_id=patient.patient_code,
            resource_type="CLINICAL_ENCOUNTER",
            resource_id=f"ENC-{patient.patient_code}-{date_slug}-{ts_slug}",
            result="SUCCESS",
            details={
                "diagnoses_count": len(diagnosis_rows),
                "prescriptions_count": len(prescription_rows),
                "evidence_codes": evidence_codes_generated,
                "saved_file": file_name
            },
            ip_address=ip_address
        )

        return DoctorEntryBatchResponse(
            success=True,
            message=f"Recorded {len(diagnosis_rows)} diagnoses and {len(prescription_rows)} prescriptions successfully with markdown document generated.",
            doctor_id=doctor.username,
            patient_code=patient.patient_code,
            recorded_at=now_str,
            diagnoses_recorded=len(diagnosis_rows),
            prescriptions_recorded=len(prescription_rows),
            evidence_codes_generated=evidence_codes_generated,
            markdown_content=markdown_content,
            markdown_file_path=saved_file_path
        )
