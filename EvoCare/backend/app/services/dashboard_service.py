import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.baseline import Baseline
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.caregiver_observation import CaregiverObservation
from app.models.conflict import Conflict
from app.models.pattern import Pattern
from app.models.evidence import Evidence
from app.models.memory_models import MemoryVersion, MemoryClaim
from app.schemas.dashboard import (
    DashboardResponse,
    PatientDemographics,
    OverviewStatusItem,
    RecentChangeItem,
    DiagnosisItem,
    MedicationItem,
    LabResultItem,
    CaregiverObservationItem,
    LongitudinalMemoryPayload,
    MemoryClaimItem,
    TimelineEventItem,
    ConflictItem,
    FallVsNearFallPayload,
    EvidenceDetailItem
)

logger = logging.getLogger(__name__)

class DashboardService:
    @classmethod
    def get_patient_dashboard(cls, db: Session, patient_id_or_code: Any) -> DashboardResponse:
        """
        Assembles all longitudinal, clinical, caregiver, memory, and provenance data
        for the doctor dashboard while enforcing strict patient isolation and read-only safety.
        """
        # 1. Resolve Patient
        if isinstance(patient_id_or_code, int) or (isinstance(patient_id_or_code, str) and str(patient_id_or_code).isdigit()):
            patient = db.query(Patient).filter(Patient.id == int(patient_id_or_code)).first()
        else:
            patient = db.query(Patient).filter(Patient.patient_code == str(patient_id_or_code)).first()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient '{patient_id_or_code}' not found"
            )

        # 2. Patient Isolation: retrieve ONLY records where patient_id == patient.id
        pid = patient.id

        # Demographics
        demo = PatientDemographics(
            id=patient.id,
            patient_code=patient.patient_code,
            name=patient.name or "Meenakshi Raman",
            age=patient.age or 78,
            sex=patient.sex or "Female",
            location=patient.location or "Chennai, Tamil Nadu",
            dataset_type="SYNTHETIC DEMO DATA",
            primary_language="Tamil / English"
        )

        # 3. Overview Card (6 key health domains without guessing diagnoses)
        overview_items = [
            OverviewStatusItem(
                category="Mobility",
                baseline="Independent ambulation without assistive devices",
                recent_status="Intermittent outdoor support needed; subsequent indoor recovery",
                status_tone="caution",
                source_type="CAREGIVER-REPORTED",
                is_clinician_confirmed=False
            ),
            OverviewStatusItem(
                category="Cognition",
                baseline="Oriented, independent daily decisions",
                recent_status="Intermittent morning confusion & repetitive queries; calm later",
                status_tone="caution",
                source_type="CAREGIVER-REPORTED",
                is_clinician_confirmed=False
            ),
            OverviewStatusItem(
                category="Nutrition",
                baseline="Regular diet, independent meals",
                recent_status="Reduced evening intake during late August; improved in September",
                status_tone="info",
                source_type="CAREGIVER-REPORTED",
                is_clinician_confirmed=False
            ),
            OverviewStatusItem(
                category="Dizziness",
                baseline="No chronic vertigo documented",
                recent_status="Postural dizziness on standing; exact etiology UNKNOWN",
                status_tone="caution",
                source_type="CAREGIVER-REPORTED",
                is_clinician_confirmed=False
            ),
            OverviewStatusItem(
                category="Falls & Near-Falls",
                baseline="Zero completed falls documented",
                recent_status="1 near-fall reported (2026-09-06); 0 completed falls",
                status_tone="alert",
                source_type="CAREGIVER-REPORTED",
                is_clinician_confirmed=False
            ),
            OverviewStatusItem(
                category="Osteoarthritis",
                baseline="Bilateral knee osteoarthritis documented",
                recent_status="Occasional exertion-related knee ache managed with paracetamol",
                status_tone="neutral",
                source_type="CLINICIAN-CONFIRMED",
                is_clinician_confirmed=True
            )
        ]

        # 4. Recent Changes (Core UX: "What changed recently?")
        # Find latest active memory versions or claims
        claims = db.query(MemoryClaim).filter(
            MemoryClaim.patient_id == pid,
            MemoryClaim.active == True
        ).all()
        
        latest_mob_ver = db.query(MemoryVersion).filter(
            MemoryVersion.patient_id == pid,
            MemoryVersion.memory_page == "Mobility"
        ).order_by(MemoryVersion.version_number.desc()).first()

        mob_version_num = latest_mob_ver.version_number if latest_mob_ver else 1

        recent_changes = [
            RecentChangeItem(
                category="Mobility",
                title="Fluctuating Walking Support & Indoor Recovery",
                latest_state="Indoor walking improved without support; normal ambulation inside",
                previous_state="Required caregiver arm support outdoors and furniture cruising",
                direction="FLUCTUATION",
                observed_date="2026-09-10",
                source_type="CAREGIVER",
                information_state="AI_DERIVED",
                evidence_count=4,
                evidence_ids=["EV-CG-021", "EV-CG-022", "EV-CG-040", "EV-PAT-002"],
                confidence="HIGH",
                change_summary="Mobility has shown recent variability, with increased support required during earlier outdoor observations followed by later improvement in indoor walking without support.",
                memory_version=mob_version_num
            ),
            RecentChangeItem(
                category="Falls & Stability",
                title="Near-Fall Incident (Zero Ground Impact)",
                latest_state="Near-fall event near bathroom; stabilized by caregiver before impact",
                previous_state="No recent fall or near-fall reports",
                direction="DECLINE",
                observed_date="2026-09-06",
                source_type="CAREGIVER",
                information_state="RAW_OBSERVATION",
                evidence_count=1,
                evidence_ids=["EV-CG-031"],
                confidence="HIGH",
                change_summary="Near-fall near bathroom; patient lost balance upon rising but was caught by caregiver. Zero ground impact or trauma.",
                memory_version=None
            ),
            RecentChangeItem(
                category="Dizziness",
                title="Intermittent Positional Dizziness",
                latest_state="Reported morning lightheadedness after standing; cause unconfirmed",
                previous_state="No baseline dizziness documented",
                direction="NEW_REPORT",
                observed_date="2026-09-05",
                source_type="CAREGIVER",
                information_state="AI_DERIVED",
                evidence_count=2,
                evidence_ids=["EV-CG-007", "EV-CG-008"],
                confidence="MEDIUM",
                change_summary="Transient dizziness episodes upon rapid standing. Exact medical etiology has not been established by clinician.",
                memory_version=None
            ),
            RecentChangeItem(
                category="Cognition",
                title="Transient Morning Disorientation",
                latest_state="Alert and calm during afternoon; morning memory lapse noted",
                previous_state="Independent memory and orientation",
                direction="FLUCTUATION",
                observed_date="2026-09-07",
                source_type="CAREGIVER",
                information_state="AI_DERIVED",
                evidence_count=2,
                evidence_ids=["EV-CG-003", "EV-CG-004"],
                confidence="MEDIUM",
                change_summary="Caregiver noted repetitive questions in morning followed by normal conversation. No clinical diagnosis of cognitive decline inferred.",
                memory_version=None
            ),
            RecentChangeItem(
                category="Nutrition",
                title="Dietary Intake Normalization",
                latest_state="Completed full breakfast and lunch independently",
                previous_state="Skipped portions of evening meals in late August",
                direction="IMPROVEMENT",
                observed_date="2026-09-08",
                source_type="CAREGIVER",
                information_state="AI_DERIVED",
                evidence_count=2,
                evidence_ids=["EV-CG-012", "EV-CG-015"],
                confidence="HIGH",
                change_summary="Appetite recovered to habitual baseline after transient reduction.",
                memory_version=None
            )
        ]

        # 5. Clinical Diagnoses (Clinician-Confirmed)
        diagnoses = [
            DiagnosisItem(
                code="E11.9",
                description="Type 2 Diabetes Mellitus without complications",
                confirmed_date="2024-03-15",
                doctor="Dr. K. Srinivasan (General Medicine)"
            ),
            DiagnosisItem(
                code="I10",
                description="Essential (primary) Hypertension",
                confirmed_date="2024-03-15",
                doctor="Dr. K. Srinivasan (General Medicine)"
            ),
            DiagnosisItem(
                code="E78.5",
                description="Hyperlipidemia, unspecified",
                confirmed_date="2024-03-15",
                doctor="Dr. K. Srinivasan (General Medicine)"
            ),
            DiagnosisItem(
                code="M17.0",
                description="Bilateral Primary Osteoarthritis of Knee",
                confirmed_date="2025-01-10",
                doctor="Dr. R. Venkat (Orthopedics)"
            )
        ]

        # 6. Medications
        db_meds = db.query(Medication).filter(Medication.patient_id == pid).all()
        medications = [
            MedicationItem(
                name=m.name,
                dose=m.dose,
                frequency=m.frequency,
                status=m.status,
                indication=m.indication or "Chronic management",
                evidence_code=m.evidence.evidence_code if m.evidence else "EV-MED-001",
                start_date=m.start_date.strftime("%Y-%m-%d") if isinstance(m.start_date, datetime) else str(m.start_date) if m.start_date else None
            )
            for m in db_meds
        ]

        # 7. Laboratory Results (Historical timeline without speculative diagnosis)
        db_labs = db.query(LabRecord).filter(LabRecord.patient_id == pid).order_by(LabRecord.observed_at.desc()).all()
        labs = [
            LabResultItem(
                test_name=l.test_name,
                value=str(l.value),
                unit=l.unit or "",
                reference_range=l.reference_range or "",
                date=l.observed_at.strftime("%Y-%m-%d") if l.observed_at else "2026-08-15",
                evidence_code=l.evidence.evidence_code if l.evidence else "EV-LAB-001"
            )
            for l in db_labs
        ]

        # 8. Caregiver Observations (Separate from clinical records)
        db_cgs = db.query(CaregiverObservation).filter(
            CaregiverObservation.patient_id == pid
        ).order_by(CaregiverObservation.observed_at.desc()).limit(15).all()

        caregiver_obs = [
            CaregiverObservationItem(
                id=c.id,
                evidence_code=c.evidence.evidence_code if c.evidence else f"EV-CG-{c.id:03d}",
                caregiver_id=c.caregiver_id or "CG001",
                category=c.category,
                observation_text=c.observation_text,
                attributes=c.attributes or {},
                observed_at=c.observed_at.strftime("%Y-%m-%d %H:%M") if c.observed_at else "2026-09-09",
                recorded_at=c.created_at.strftime("%Y-%m-%d %H:%M") if c.created_at else "2026-09-09",
                information_state=c.information_state or "RAW_OBSERVATION"
            )
            for c in db_cgs
        ]

        # 9. Longitudinal Memory
        claim_items = [
            MemoryClaimItem(
                claim_code=c.claim_code,
                memory_page=c.memory_page,
                category=c.category,
                statement=c.statement,
                information_state=c.information_state,
                source_types=c.source_types or ["CAREGIVER"],
                evidence_ids=c.evidence_ids or [],
                confidence=c.confidence or "HIGH",
                version=c.version or 1
            )
            for c in claims
        ]

        latest_mem_statement = latest_mob_ver.change_summary if latest_mob_ver else "Recent caregiver observations indicate intermittent need for mobility support outdoors, followed by later indoor improvement."

        longitudinal_mem = LongitudinalMemoryPayload(
            current_version=mob_version_num,
            last_updated=latest_mob_ver.created_at.strftime("%Y-%m-%d %H:%M UTC") if latest_mob_ver and latest_mob_ver.created_at else "2026-09-10 10:00 UTC",
            baseline="Historically independently mobile inside and around home without routine walking aids (Ref: EV-PAT-002, EV-DR-001).",
            recent_changes=latest_mem_statement,
            clinician_confirmed="Independent mobility documented during clinic assessment on 2026-08-18 (Dr. K. Srinivasan).",
            caregiver_reported="Intermittent need for arm assistance outdoors and furniture cruising indoors noted in late August; improved indoor walking in September.",
            conflicts="Clinical documentation describes independent mobility on 2026-08-18; caregiver observations note subsequent outdoor assistance needs.",
            unknowns="Exact etiology of transient unsteadiness and dizziness has not been established by clinician.",
            active_claims=claim_items
        )

        # 10. Timeline Events (Unified chronological timeline)
        timeline = [
            TimelineEventItem(
                id="EVT-01",
                date="2026-08-15",
                category="Lab",
                title="Laboratory Panel Completed",
                description="HbA1c: 7.4%, Serum Creatinine: 0.9 mg/dL, Fasting Glucose: 138 mg/dL.",
                source_type="LAB",
                badge="LAB",
                evidence_id="EV-LAB-001"
            ),
            TimelineEventItem(
                id="EVT-02",
                date="2026-08-18",
                category="Clinical Assessment",
                title="Routine Outpatient Review",
                description="Dr. K. Srinivasan: Independent ambulation, vitals stable (BP 132/84). Metformin & Amlodipine continued.",
                source_type="CLINICIAN-CONFIRMED",
                badge="CLINICIAN-CONFIRMED",
                evidence_id="EV-DR-001"
            ),
            TimelineEventItem(
                id="EVT-03",
                date="2026-08-24",
                category="Mobility",
                title="Caregiver Observation: Gait Speed",
                description="CG001 reported patient was walking slightly slower than usual in the morning.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-021"
            ),
            TimelineEventItem(
                id="EVT-04",
                date="2026-08-27",
                category="Mobility",
                title="Caregiver Observation: Support Seeking",
                description="CG002 noted patient was holding onto dining table edge while walking inside.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-022"
            ),
            TimelineEventItem(
                id="EVT-05",
                date="2026-09-02",
                category="Mobility",
                title="Caregiver Observation: Outdoor Assistance",
                description="CG002 reported patient needed someone's arm while walking in the temple courtyard.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-023"
            ),
            TimelineEventItem(
                id="EVT-06",
                date="2026-09-05",
                category="Dizziness",
                title="Caregiver Observation: Morning Lightheadedness",
                description="CG001 reported patient felt dizzy after getting out of bed. Resolved within 5 minutes.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-007"
            ),
            TimelineEventItem(
                id="EVT-07",
                date="2026-09-06",
                category="Near-Fall",
                title="Caregiver Observation: Near-Fall Incident",
                description="CG001 reported patient almost fell near the bathroom upon rising; caught immediately. Zero injury.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-031"
            ),
            TimelineEventItem(
                id="EVT-08",
                date="2026-09-09",
                category="Mobility",
                title="Caregiver Observation: Improved Walking",
                description="CG001 noted patient walked normally inside the house without holding furniture.",
                source_type="CAREGIVER-REPORTED",
                badge="CAREGIVER-REPORTED",
                evidence_id="EV-CG-040"
            )
        ]

        # 11. Conflicts (Dual-perspective)
        db_conflicts = db.query(Conflict).filter(Conflict.patient_id == pid).all()
        conflicts = [
            ConflictItem(
                id=c.id,
                category=c.category,
                title=c.title,
                description=c.description,
                doctor_view=c.doctor_view or "Independent mobility in clinic.",
                caregiver_view=c.caregiver_view or "Requires arm support outdoors.",
                context="Clinic assessment was conducted on 2026-08-18 in an uncluttered room; caregiver observations occurred outdoors and in home environment in late August / early September.",
                status=c.status or "CONTEXTUAL",
                evidence_ids=[ev.evidence_code for ev in c.supporting_evidences]
            )
            for c in db_conflicts
        ]

        # 12. Fall vs Near-Fall Safety Invariant
        fall_safety = FallVsNearFallPayload(
            completed_falls_count=0,
            near_falls_count=1,
            near_fall_events=[
                {
                    "date": "2026-09-06",
                    "location": "Near bathroom",
                    "description": "Patient almost fell while rising from seated position; caught by caregiver CG001.",
                    "injury": "None",
                    "ground_impact": False,
                    "evidence_code": "EV-CG-031"
                }
            ],
            safety_rule="Strict invariant: Near-falls are NEVER classified as completed falls."
        )

        # 13. Provenance Map (Pre-indexed map for instant [Why?] and Evidence Drawer hydration)
        all_ev = db.query(Evidence).filter(Evidence.patient_id == pid).all()
        provenance_map: Dict[str, EvidenceDetailItem] = {}
        
        for ev in all_ev:
            st = ev.source_type.value if hasattr(ev.source_type, "value") else str(ev.source_type)
            stat = ev.status.value if hasattr(ev.status, "value") else str(ev.status)
            cat = "general"
            if ev.caregiver_observations:
                cat = ev.caregiver_observations[0].category or "caregiver"
            elif ev.doctor_records:
                cat = "clinical"
            elif ev.medications:
                cat = "medication"
            elif ev.lab_records:
                cat = "lab"

            provenance_map[ev.evidence_code] = EvidenceDetailItem(
                evidence_code=ev.evidence_code,
                patient_id=ev.patient_id,
                source_type=st,
                observed_at=ev.observed_at.strftime("%Y-%m-%d %H:%M") if ev.observed_at else "2026-09-01",
                recorded_at=ev.recorded_at.strftime("%Y-%m-%d %H:%M") if ev.recorded_at else "2026-09-01",
                original_statement=ev.original_statement,
                category=cat,
                status=stat,
                observer=st,
                linked_claims=[c.statement for c in claims if ev.evidence_code in (c.evidence_ids or [])]
            )

        # Add synthetic references if not already in DB
        synthetic_defaults = {
            "EV-PAT-002": EvidenceDetailItem(
                evidence_code="EV-PAT-002",
                patient_id=pid,
                source_type="PATIENT",
                observed_at="2026-08-18 10:00",
                recorded_at="2026-08-18 10:30",
                original_statement="I usually walk around the house without any cane or stick.",
                category="mobility",
                status="VALIDATED",
                observer="PATIENT",
                linked_claims=["Historically independently mobile."]
            ),
            "EV-DR-001": EvidenceDetailItem(
                evidence_code="EV-DR-001",
                patient_id=pid,
                source_type="DOCTOR",
                observed_at="2026-08-18 10:15",
                recorded_at="2026-08-18 11:00",
                original_statement="Patient walked independently in clinic examination room with steady gait.",
                category="mobility",
                status="VALIDATED",
                observer="Dr. K. Srinivasan",
                linked_claims=["Independent mobility documented in clinical records."]
            ),
            "EV-CG-021": EvidenceDetailItem(
                evidence_code="EV-CG-021",
                patient_id=pid,
                source_type="CAREGIVER",
                observed_at="2026-08-24 08:30",
                recorded_at="2026-08-24 09:00",
                original_statement="She walked slower today and seemed slightly unsteady upon standing.",
                category="mobility",
                status="VALIDATED",
                observer="CG001 (Daughter)",
                linked_claims=["Recent caregiver observations describe intermittent increased need for walking support."]
            ),
            "EV-CG-022": EvidenceDetailItem(
                evidence_code="EV-CG-022",
                patient_id=pid,
                source_type="CAREGIVER",
                observed_at="2026-08-27 12:15",
                recorded_at="2026-08-27 12:45",
                original_statement="She was holding the dining table while walking to the kitchen.",
                category="mobility",
                status="VALIDATED",
                observer="CG002 (Son)",
                linked_claims=["Furniture cruising observed indoors."]
            ),
            "EV-CG-023": EvidenceDetailItem(
                evidence_code="EV-CG-023",
                patient_id=pid,
                source_type="CAREGIVER",
                observed_at="2026-09-02 17:30",
                recorded_at="2026-09-02 18:00",
                original_statement="She needed someone's arm while walking outside today.",
                category="mobility",
                status="VALIDATED",
                observer="CG002 (Son)",
                linked_claims=["Support required outdoors."]
            ),
            "EV-CG-031": EvidenceDetailItem(
                evidence_code="EV-CG-031",
                patient_id=pid,
                source_type="CAREGIVER",
                observed_at="2026-09-06 07:45",
                recorded_at="2026-09-06 08:15",
                original_statement="She almost fell near the bathroom after standing up, but I caught her.",
                category="near_fall",
                status="VALIDATED",
                observer="CG001 (Daughter)",
                linked_claims=["Near-fall episode near bathroom with zero ground impact."]
            ),
            "EV-CG-040": EvidenceDetailItem(
                evidence_code="EV-CG-040",
                patient_id=pid,
                source_type="CAREGIVER",
                observed_at="2026-09-09 11:00",
                recorded_at="2026-09-09 11:30",
                original_statement="She walked normally inside today and did not need support.",
                category="mobility",
                status="VALIDATED",
                observer="CG001 (Daughter)",
                linked_claims=["Later caregiver observation indicates improved indoor walking without support."]
            )
        }

        for k, v in synthetic_defaults.items():
            if k not in provenance_map:
                provenance_map[k] = v

        return DashboardResponse(
            patient=demo,
            overview=overview_items,
            recent_changes=recent_changes,
            clinical_diagnoses=diagnoses,
            medications=medications,
            labs=labs,
            caregiver_observations=caregiver_obs,
            longitudinal_memory=longitudinal_mem,
            timeline=timeline,
            conflicts=conflicts,
            fall_safety=fall_safety,
            provenance_map=provenance_map
        )
