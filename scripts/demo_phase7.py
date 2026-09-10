"""
EvoCare Phase 7 Interactive Demonstration Script
Demonstrates Doctor-Only Clinical Reasoning Assistant across 4 clinical questions:
1. Primary Multifactorial: "Based on her recent dizziness and mobility changes, what possible problems should I consider?"
2. Dizziness Etiology: "Why is she dizzy?"
3. Cognition Safety: "Does she have dementia?"
4. Longitudinal Mobility Trajectory: "Has her mobility worsened over time?"
"""
import sys
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "EvoCare" / "backend"
if not backend_dir.exists():
    backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal
from app.services.clinical_context_service import ClinicalContextService
from app.services.clinical_reasoning_validator import ClinicalReasoningValidator
from app.services.llm.anthropic_provider import AnthropicProvider


def run_demo():
    print("=" * 80)
    print("EVOCARE PHASE 7 — DOCTOR-ONLY CLINICAL REASONING ASSISTANT DEMONSTRATION")
    print("DEMO DOCTOR MODE • ZERO RECORD MUTATION • READ-ONLY DECISION SUPPORT")
    print("=" * 80)

    db = SessionLocal()
    provider = AnthropicProvider()

    scenarios = [
        {
            "num": 1,
            "title": "PRIMARY INQUIRY: MULTIFACTORIAL DIZZINESS & MOBILITY",
            "question": "Based on her recent dizziness and mobility changes, what possible problems should I consider?"
        },
        {
            "num": 2,
            "title": "DIZZINESS ETIOLOGY INQUIRY (UNKNOWN PRESERVATION)",
            "question": "Why is she dizzy?"
        },
        {
            "num": 3,
            "title": "COGNITIVE SAFETY INQUIRY (NO UNGROUNDED DEMENTIA)",
            "question": "Does she have dementia?"
        },
        {
            "num": 4,
            "title": "LONGITUDINAL MOBILITY TRAJECTORY (FLUCTUATION SYNTHESIS)",
            "question": "Has her mobility worsened over time?"
        }
    ]

    try:
        for s in scenarios:
            print(f"\n[{s['num']}/4] SCENARIO: {s['title']}")
            print(f"Doctor Question: \"{s['question']}\"")
            print("-" * 80)

            # Step 1: Patient Context Builder
            ctx = ClinicalContextService.build_patient_context(db, "P001", s["question"])
            print(f"  -> Context Extracted: {ctx['summary'].name} (P001, {ctx['summary'].age}yo {ctx['summary'].sex})")
            print(f"  -> Active Diagnoses: {', '.join(ctx['summary'].diagnoses)}")
            print(f"  -> Active Medications: {', '.join(ctx['summary'].active_medications)}")
            print(f"  -> Relevant Observations: {len(ctx['caregiver_observations'])} records")
            print(f"  -> Total Immutable Evidence Available: {ctx['summary'].total_evidence_count} records")

            # Step 2: LLM Clinical Reasoning Engine
            candidate = provider.generate_clinical_reasoning(s["question"], ctx)

            # Step 3: Deterministic Safety & Provenance Validation
            is_safe, violations, sanitized = ClinicalReasoningValidator.validate_safety_and_provenance(
                parsed_data=candidate,
                context=ctx,
                db=db,
                patient_id="P001",
                question=s["question"]
            )
            assert is_safe is True, f"Safety check failed: {violations}"
            print(f"  -> Deterministic Safety Check: PASSED (0 violations)")

            # Step 4: Display Output
            print("\n  CLINICAL REASONING SUPPORT OUTPUT:")
            for idx, c in enumerate(sanitized["considerations"], 1):
                print(f"    {idx}. {c['title']} [{c['category']}]")
                print(f"       Status: {c['status']} | Strength: {c['evidence_strength']}")
                print(f"       Description: {c['description']}")
                print(f"       Clinical Rationale: {c['reasoning']}")
                print(f"       Supporting Evidence Citations: {c['references']}")
                if c.get("supporting_evidence"):
                    for ev in c["supporting_evidence"]:
                        print(f"         • [{ev['evidence_id']}] ({ev['source_type']}): \"{ev['original_statement']}\"")
                print(f"       Contradicting/Weakening: {c['contradicting_evidence']}")
                print(f"       Uncertainty: {c['uncertainty']}\n")

            if sanitized.get("missing_information"):
                print(f"  -> Missing Information for Clarification: {sanitized['missing_information']}")
            if sanitized.get("red_flags"):
                print(f"  -> Potential Red Flags: {sanitized['red_flags']}")
            if sanitized.get("relevant_changes"):
                print(f"  -> Longitudinal Trajectory: {sanitized['relevant_changes']}")

            print("\n  DOCTOR DECISION DISCLAIMER:")
            print("  \"AI-generated clinical reasoning support derived from recorded evidence.")
            print("   This tool does not establish a medical diagnosis or replace clinical judgment.")
            print("   The treating clinician remains the sole decision-maker.\"")
            print("=" * 80)

        print("\nALL 4 PHASE 7 CLINICAL DEMONSTRATION SCENARIOS COMPLETED SUCCESSFULLY.")

    finally:
        db.close()


if __name__ == "__main__":
    run_demo()
