"""
EvoCare Phase 6 Demonstration Script: Doctor Dashboard & Longitudinal Patient View
Demonstrates:
1. Backend Aggregated Dashboard Endpoint for Patient P001
2. Patient Overview & Baseline Status
3. Clinician-Confirmed Context (Diagnoses, Active Medications, Lab Timeline)
4. Caregiver-Reported Observations (Visually Separated)
5. Recent Changes Panel with Directional Trajectory & Confidence
6. Longitudinal Evolving Memory with Version Tracking & Unknowns
7. Chronological Patient Timeline
8. Contextual Discrepancies & Conflict Analysis
9. [Why?] Provenance Tracing from Derived Claim -> Exact Immutable Evidence
10. Fall vs Near-Fall Safety Invariant
11. Read-Only Invariant Enforcement
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "EvoCare" / "backend"
if not backend_dir.exists():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.services.dashboard_service import DashboardService

def main():
    print("=" * 80)
    print("EVOCARE PHASE 6: DOCTOR DASHBOARD & LONGITUDINAL PATIENT VIEW DEMO")
    print("=" * 80)

    init_db()
    db = SessionLocal()

    try:
        # Step 1: Query Aggregated Dashboard Endpoint
        print("\n--- STEP 1: Querying Aggregated Dashboard Endpoint for Patient P001 ---")
        dashboard = DashboardService.get_patient_dashboard(db, "P001")
        p = dashboard.patient
        print(f"Patient Name: {p.name} ({p.patient_code})")
        print(f"Demographics: {p.age} years • {p.sex} • {p.location}")
        print(f"Dataset Classification: [{p.dataset_type}]")

        # Step 2: Patient Health Domain Overview
        print("\n--- STEP 2: Longitudinal Health Domain Overview (6 Dimensions) ---")
        for item in dashboard.overview:
            print(f"  [{item.category.upper()}]")
            print(f"    Baseline: {item.baseline}")
            print(f"    Recent:   {item.recent_status} (Source: {item.source_type})")

        # Step 3: Priority Doctor View: Recent Changes
        print("\n--- STEP 3: Priority Doctor View: Recent Changes ---")
        for change in dashboard.recent_changes:
            print(f"\n  * {change.title} [{change.direction}]")
            print(f"    Previous State: {change.previous_state}")
            print(f"    Latest State:   {change.latest_state}")
            print(f"    Synthesized:    {change.change_summary}")
            print(f"    Evidence Count: {change.evidence_count} records {change.evidence_ids} (Confidence: {change.confidence})")

        # Step 4: Clinical Records vs Caregiver Separation
        print("\n--- STEP 4: Clinician-Confirmed Records ---")
        print("  Diagnoses:")
        for d in dashboard.clinical_diagnoses:
            print(f"    - {d.code}: {d.description} (Confirmed: {d.confirmed_date} by {d.doctor})")

        print("\n  Active Medications:")
        for m in dashboard.medications:
            print(f"    - {m.name} {m.dose} ({m.frequency}) - Indication: {m.indication} [Status: {m.status}]")

        print("\n  Laboratory Timeline (Historical Values):")
        for l in dashboard.labs:
            print(f"    - {l.date}: {l.test_name} = {l.value} {l.unit} (Ref: {l.reference_range})")

        # Step 5: Caregiver Observations (Separated Feed)
        print("\n--- STEP 5: Caregiver Observations Feed (Separated from Clinical Context) ---")
        for obs in dashboard.caregiver_observations[:4]:
            print(f"  [{obs.evidence_code}] {obs.observed_at} ({obs.caregiver_id}) Category: {obs.category}")
            print(f"    \"{obs.observation_text}\"")

        # Step 6: Longitudinal Evolving Memory
        print("\n--- STEP 6: Longitudinal Memory & Version State ---")
        mem = dashboard.longitudinal_memory
        print(f"  Current Memory Version: {mem.current_version} (Last Synchronized: {mem.last_updated})")
        print(f"  Baseline:            {mem.baseline}")
        print(f"  Recent Trajectory:   {mem.recent_changes}")
        print(f"  Clinician Notes:     {mem.clinician_confirmed}")
        print(f"  Known Unknowns:      {mem.unknowns}")

        # Step 7: Chronological Timeline
        print("\n--- STEP 7: Unified Patient Timeline ---")
        for evt in dashboard.timeline[:6]:
            print(f"  [{evt.date}] {evt.title} [{evt.badge}]")
            print(f"    {evt.description}")

        # Step 8: Contextual Discrepancies & Conflict Analysis
        print("\n--- STEP 8: Contextual Discrepancies & Conflict Analysis ---")
        for conf in dashboard.conflicts:
            print(f"  Conflict: {conf.title} (Category: {conf.category})")
            print(f"    Doctor View:    {conf.doctor_view}")
            print(f"    Caregiver View: {conf.caregiver_view}")
            print(f"    Context:        {conf.context}")
            print(f"    Status:         {conf.status} (Evidence: {conf.evidence_ids})")

        # Step 9: [Why?] Provenance Tracing
        print("\n--- STEP 9: [Why?] Provenance & Derivation Tracing ---")
        mob_change = dashboard.recent_changes[0]
        print(f"  Doctor clicks [Why?] on claim:")
        print(f"    \"{mob_change.change_summary}\"")
        print(f"  Information State: {mob_change.information_state}")
        print(f"  Supporting Evidence Breakdown:")
        for ev_code in mob_change.evidence_ids:
            ev_detail = dashboard.provenance_map.get(ev_code)
            if ev_detail:
                print(f"    -> {ev_code} ({ev_detail.observed_at}) [{ev_detail.source_type}]:")
                print(f"       \"{ev_detail.original_statement}\"")

        # Step 10: Fall vs Near-Fall Invariant
        print("\n--- STEP 10: Safety Gating: Fall vs Near-Fall ---")
        fs = dashboard.fall_safety
        print(f"  Completed Falls: {fs.completed_falls_count}")
        print(f"  Near-Falls:      {fs.near_falls_count}")
        print(f"  Safety Invariant: {fs.safety_rule}")

        print("\n" + "=" * 80)
        print("PHASE 6 DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 80)

    finally:
        db.close()

if __name__ == "__main__":
    main()
