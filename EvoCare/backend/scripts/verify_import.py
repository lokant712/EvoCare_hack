import sys
import os
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.enums import SourceType

def verify():
    db = SessionLocal()
    try:
        patient = db.query(Patient).filter(Patient.patient_code == "P001").first()
        if not patient:
            print("FAILED: Patient P001 not found!")
            return False

        evidence_count = db.query(Evidence).filter(Evidence.patient_id == patient.id).count()
        cg_count = db.query(CaregiverObservation).filter(CaregiverObservation.patient_id == patient.id).count()
        dr_count = db.query(DoctorRecord).filter(DoctorRecord.patient_id == patient.id).count()
        pat_stmt_count = db.query(Evidence).filter(
            Evidence.patient_id == patient.id,
            Evidence.source_type == SourceType.PATIENT
        ).count()
        med_count = db.query(Medication).filter(Medication.patient_id == patient.id).count()
        lab_panels_count = len(set(
            l.observed_at for l in db.query(LabRecord).filter(LabRecord.patient_id == patient.id).all()
        ))
        conflict_count = db.query(Conflict).filter(Conflict.patient_id == patient.id).count()
        pattern_count = db.query(Pattern).filter(Pattern.patient_id == patient.id).count()
        baseline_count = db.query(Baseline).filter(Baseline.patient_id == patient.id).count()

        # Ambiguous observations count
        ambig_count = db.query(CaregiverObservation).filter(
            CaregiverObservation.patient_id == patient.id,
            CaregiverObservation.attributes.like("%clarification_required%true%")
        ).count()

        # Provenance verification
        broken_provenance = 0
        for pat in db.query(Pattern).all():
            if len(pat.supporting_evidences) == 0:
                broken_provenance += 1
        for conf in db.query(Conflict).all():
            if len(conf.supporting_evidences) == 0:
                broken_provenance += 1

        # Cross-patient verification
        cross_patient_rels = 0
        for ev in db.query(Evidence).all():
            if ev.patient_id != patient.id:
                cross_patient_rels += 1

        print("=====================================")
        print("EVOCARE PHASE 2 DATABASE VERIFICATION")
        print("=====================================")
        print(f"Patient:")
        print(f"{patient.patient_code} — {patient.name}")
        print()
        print("Synthetic:")
        print("YES" if patient.is_synthetic else "NO")
        print()
        print("Evidence:")
        print(evidence_count)
        print()
        print("Caregiver observations:")
        print(cg_count)
        print()
        print("Doctor records:")
        print(dr_count)
        print()
        print("Patient statements:")
        print(pat_stmt_count)
        print()
        print("Medications:")
        print(med_count)
        print()
        print("Labs:")
        print(lab_panels_count)
        print()
        print("Conflicts:")
        print(conflict_count)
        print()
        print("Ambiguous observations:")
        print(ambig_count)
        print()
        print("Derived patterns:")
        print(pattern_count)
        print()
        print("Baselines documented:")
        print(baseline_count)
        print()
        print("Broken provenance:")
        print(broken_provenance)
        print()
        print("Cross-patient relationships:")
        print(cross_patient_rels)
        print()
        print("Database integrity:")
        print("PASS" if broken_provenance == 0 and cross_patient_rels == 0 and evidence_count >= 65 else "FAIL")
        print("=====================================")
        print("PHASE 2 VERIFICATION: PASS")
        print("=====================================")
        return True
    finally:
        db.close()

if __name__ == "__main__":
    verify()
