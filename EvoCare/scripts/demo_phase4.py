"""
EvoCare Phase 4 Demonstration Script
Demonstrates LLM-assisted interpretation, strict safety validation, clarification workflow,
evidence generation with provenance, and deterministic fallback behavior.
Runs offline using MockLLMProvider without requiring an Anthropic API key.
"""
import sys
import os
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.core.database import SessionLocal, init_db
from app.services.llm import MockLLMProvider, LLMStatus, AnthropicProvider
from app.services.observation_pipeline_service import ObservationPipelineService

def main():
    print("=" * 70)
    print("EVOCARE PHASE 4 DEMONSTRATION: LLM OBSERVATION INTELLIGENCE")
    print("=" * 70)

    init_db()
    db = SessionLocal()

    try:
        # 1. SETUP MOCK LLM PROVIDER
        mock_provider = MockLLMProvider()
        ObservationPipelineService.set_llm_provider(mock_provider)

        print("\n--- STEP 1: Caregiver Input & LLM-Assisted Extraction ---")
        caregiver_text = "She is dizzy."
        print(f"Input text: '{caregiver_text}'")
        print("Processing mode: LLM")

        start_res = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text=caregiver_text,
            caregiver_id="CG001",
            processing_mode="LLM"
        )

        session_id = start_res["session_id"]
        print(f"\nSession Created: {start_res['session_code']} (ID: {session_id})")
        print(f"Detected Category: {start_res['category']}")
        print(f"Processing Method: {start_res['processing_method']}")
        print(f"Missing Fields Detected: {start_res['missing_fields']}")
        print(f"Next Clarification Question: {start_res['next_question']['question']}")
        print(f"Options: {start_res['next_question']['options']}")

        print("\n--- STEP 2: Caregiver Answers Clarification Questions ---")
        # Answer severity
        ans1 = ObservationPipelineService.answer_question(
            db=db,
            session_id=session_id,
            field_name="severity",
            answer_text="Mild"
        )
        print(f"Answered '{ans1.field_name}': {ans1.answer}")

        # Answer duration
        ans2 = ObservationPipelineService.answer_question(
            db=db,
            session_id=session_id,
            field_name="duration",
            answer_text="A few seconds"
        )
        print(f"Answered '{ans2.field_name}': {ans2.answer}")

        # Answer onset
        ans3 = ObservationPipelineService.answer_question(
            db=db,
            session_id=session_id,
            field_name="onset",
            answer_text="After getting out of bed / standing up"
        )
        print(f"Answered '{ans3.field_name}': {ans3.answer}")

        print("\n--- STEP 3: Session Completion & Structured Evidence Ingestion ---")
        comp_res = ObservationPipelineService.complete_session(db=db, session_id=session_id)
        print(f"Status: {comp_res['status']}")
        print(f"Generated Evidence Code: {comp_res['evidence_code']}")
        print(f"Structured Attributes: {comp_res['structured_observation']['attributes']}")
        print(f"Etiology: {comp_res['structured_observation']['etiology']}")
        print(f"Clinical Diagnoses Inferred: {comp_res['structured_observation']['clinical_diagnoses_inferred']}")

        print("\n--- STEP 4: Fallback Behavior Demonstration (LLM Unavailable) ---")
        fallback_provider = AnthropicProvider(api_key="", enabled=True)
        fallback_res = ObservationPipelineService.start_session(
            db=db,
            patient_id_or_code="P001",
            raw_text="She almost fell near the bathroom.",
            caregiver_id="CG001",
            processing_mode="AUTO",
            llm_provider=fallback_provider
        )
        print(f"Input text: 'She almost fell near the bathroom.' (API Key missing)")
        print(f"Resulting Processing Method: {fallback_res['processing_method']}")
        print(f"Category Classified: {fallback_res['category']}")
        print(f"Session Status: {fallback_res['status']}")

        print("\n" + "=" * 70)
        print("DEMONSTRATION COMPLETED SUCCESSFULLY")
        print("=" * 70)

    finally:
        ObservationPipelineService.set_llm_provider(None)
        db.close()

if __name__ == "__main__":
    main()
