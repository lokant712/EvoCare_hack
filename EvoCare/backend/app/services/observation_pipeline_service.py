import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.observation import Observation
from app.models.caregiver_observation import CaregiverObservation
from app.models.audit import AuditLog
from app.models.clarification import SessionStatus, ClarificationSession, ClarificationQuestion, ClarificationAnswer
from app.models.enums import SourceType, InformationState, EvidenceStatus
from app.services.clarification_engine import ClarificationEngine
from app.services.llm.schemas import (
    ProcessingMode,
    ProcessingMethod,
    LLMStatus,
    ParsedCaregiverObservation,
    CertaintyState,
    ConfidenceLevel,
)
from app.services.llm.provider import LLMProvider
from app.services.llm.resilient_provider import ResilientLLMProvider

class ObservationPipelineService:
    # Active default LLM provider instance (can be overridden in tests via set_llm_provider)
    _default_llm_provider: Optional[LLMProvider] = None

    @classmethod
    def set_llm_provider(cls, provider: Optional[LLMProvider]):
        cls._default_llm_provider = provider

    @classmethod
    def get_llm_provider(cls) -> LLMProvider:
        if cls._default_llm_provider is not None:
            return cls._default_llm_provider
        return ResilientLLMProvider()

    @classmethod
    def start_session(
        cls,
        db: Session,
        patient_id_or_code: Any,
        raw_text: str,
        caregiver_id: str = "CG001",
        processing_mode: str = "AUTO",
        llm_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
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

        provider = llm_provider or cls.get_llm_provider()
        mode = processing_mode.upper() if isinstance(processing_mode, str) else "AUTO"

        category: str = "mobility"
        initial_extracted: Dict[str, Any] = {}
        missing_fields: List[str] = []
        processing_method: str = ProcessingMethod.DETERMINISTIC.value
        parsed_llm_obs: Optional[ParsedCaregiverObservation] = None
        certainty: str = CertaintyState.CONFIRMED.value
        confidence: str = ConfidenceLevel.HIGH.value

        # 2. Execution Routing based on processing_mode
        if mode in ("AUTO", "LLM"):
            patient_context = {
                "patient_code": patient.patient_code,
                "age": getattr(patient, "age", 79),
                "sex": getattr(patient, "gender", "F")
            }
            llm_result = provider.extract_observation(raw_text, patient_context)

            if llm_result.status == LLMStatus.SUCCESS and llm_result.parsed_observation:
                parsed_llm_obs = llm_result.parsed_observation
                category = parsed_llm_obs.category.value
                processing_method = ProcessingMethod.LLM_ASSISTED.value
                certainty = parsed_llm_obs.certainty.value
                confidence = parsed_llm_obs.confidence.value

                # Populate initial extracted from LLM (only non-unknown fields)
                if parsed_llm_obs.severity and parsed_llm_obs.severity.upper() != "UNKNOWN":
                    initial_extracted["severity"] = parsed_llm_obs.severity
                if parsed_llm_obs.duration and parsed_llm_obs.duration.upper() != "UNKNOWN":
                    initial_extracted["duration"] = parsed_llm_obs.duration
                if parsed_llm_obs.onset and parsed_llm_obs.onset.upper() != "UNKNOWN":
                    initial_extracted["onset"] = parsed_llm_obs.onset
                if parsed_llm_obs.context and parsed_llm_obs.context.upper() != "UNKNOWN":
                    initial_extracted["context"] = parsed_llm_obs.context
                if parsed_llm_obs.functional_impact and parsed_llm_obs.functional_impact.upper() != "UNKNOWN":
                    initial_extracted["functional_impact"] = parsed_llm_obs.functional_impact
                if parsed_llm_obs.associated_details:
                    initial_extracted.update(parsed_llm_obs.associated_details)

                # Redundant question prevention: use clarification_fields or compute missing
                if parsed_llm_obs.clarification_fields:
                    missing_fields = [f for f in parsed_llm_obs.clarification_fields if f not in initial_extracted]
                else:
                    missing_fields = ClarificationEngine.get_missing_fields(category, initial_extracted)

            else:
                # Safe Fallback to Deterministic Parser
                processing_method = ProcessingMethod.LLM_FALLBACK.value if mode == "LLM" or llm_result.status != LLMStatus.LLM_UNAVAILABLE else ProcessingMethod.DETERMINISTIC.value
                if mode == "AUTO" and llm_result.status != LLMStatus.SUCCESS:
                    processing_method = ProcessingMethod.LLM_FALLBACK.value
                
                category = ClarificationEngine.detect_category(raw_text)
                initial_extracted = ClarificationEngine.extract_initial_fields(category, raw_text)
                missing_fields = ClarificationEngine.get_missing_fields(category, initial_extracted)

                # Check uncertainty in text
                t = raw_text.lower()
                if "i think" in t or "maybe" in t or "perhaps" in t or "seems like" in t:
                    certainty = CertaintyState.UNCERTAIN.value
                    confidence = ConfidenceLevel.LOW.value

        else:  # DETERMINISTIC
            processing_method = ProcessingMethod.DETERMINISTIC.value
            category = ClarificationEngine.detect_category(raw_text)
            initial_extracted = ClarificationEngine.extract_initial_fields(category, raw_text)
            missing_fields = ClarificationEngine.get_missing_fields(category, initial_extracted)

            t = raw_text.lower()
            if "i think" in t or "maybe" in t or "perhaps" in t or "seems like" in t:
                certainty = CertaintyState.UNCERTAIN.value
                confidence = ConfidenceLevel.LOW.value

        # Generate clarification question templates
        question_templates = ClarificationEngine.generate_questions(category, missing_fields)

        # 3. Create Session Record
        session_code = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        sess = ClarificationSession(
            session_code=session_code,
            patient_id=patient.id,
            raw_text=raw_text,
            detected_category=category,
            status=SessionStatus.PENDING if missing_fields else SessionStatus.IN_PROGRESS,
            extracted_data={
                "initial": initial_extracted,
                "caregiver_id": caregiver_id,
                "processing_method": processing_method,
                "certainty": certainty,
                "confidence": confidence,
                "llm_parsed": parsed_llm_obs.model_dump() if parsed_llm_obs else None
            },
            started_at=datetime.now(timezone.utc)
        )
        db.add(sess)
        db.flush()

        # 4. Create Question rows
        q_rows = []
        for q in question_templates:
            q_row = ClarificationQuestion(
                session_id=sess.id,
                question=q["question"],
                field_name=q["field_name"],
                required=q["required"],
                options=q.get("options", [])
            )
            db.add(q_row)
            q_rows.append(q_row)

        db.commit()
        db.refresh(sess)

        next_q = None
        if q_rows:
            next_q = {
                "id": q_rows[0].id,
                "field_name": q_rows[0].field_name,
                "question": q_rows[0].question,
                "required": q_rows[0].required,
                "options": q_rows[0].options
            }

        obs_dict = {
            "category": category,
            "extracted_attributes": initial_extracted,
            "certainty": certainty,
            "confidence": confidence,
            "requires_clarification": len(missing_fields) > 0,
            "missing_fields": missing_fields
        }

        return {
            "session_id": sess.id,
            "session_code": sess.session_code,
            "patient_id": patient.id,
            "patient_code": patient.patient_code,
            "category": category,
            "missing_fields": missing_fields,
            "questions": [
                {
                    "id": q.id,
                    "field_name": q.field_name,
                    "question": q.question,
                    "required": q.required,
                    "options": q.options
                }
                for q in q_rows
            ],
            "status": sess.status,
            "processing_method": processing_method,
            "next_question": next_q,
            "observation": obs_dict
        }

    @staticmethod
    def get_session(db: Session, session_id: int) -> ClarificationSession:
        sess = db.query(ClarificationSession).filter(ClarificationSession.id == session_id).first()
        if not sess:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Clarification session with id {session_id} not found"
            )
        return sess

    @staticmethod
    def answer_question(db: Session, session_id: int, answer_text: str, question_id: int = None, field_name: str = None) -> ClarificationAnswer:
        sess = db.query(ClarificationSession).filter(ClarificationSession.id == session_id).first()
        if not sess:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")
        if sess.status == SessionStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session is already completed")

        target_field = field_name
        q_row = None
        if question_id:
            q_row = db.query(ClarificationQuestion).filter(ClarificationQuestion.id == question_id).first()
            if q_row:
                target_field = q_row.field_name

        if not target_field:
            target_field = "general_clarification"

        # Check existing answer
        existing_ans = db.query(ClarificationAnswer).filter(
            ClarificationAnswer.session_id == session_id,
            ClarificationAnswer.field_name == target_field
        ).first()

        if existing_ans:
            existing_ans.answer = answer_text
            existing_ans.answered_at = datetime.now(timezone.utc)
            ans = existing_ans
        else:
            ans = ClarificationAnswer(
                session_id=session_id,
                question_id=question_id,
                field_name=target_field,
                answer=answer_text,
                answered_at=datetime.now(timezone.utc)
            )
            db.add(ans)

        sess.status = SessionStatus.IN_PROGRESS
        db.commit()
        db.refresh(ans)
        return ans

    @staticmethod
    def complete_session(db: Session, session_id: int) -> Dict[str, Any]:
        sess = db.query(ClarificationSession).filter(ClarificationSession.id == session_id).first()
        if not sess:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Session {session_id} not found")
        if sess.status == SessionStatus.COMPLETED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Session already completed")

        patient = db.query(Patient).filter(Patient.id == sess.patient_id).first()
        caregiver_id = sess.extracted_data.get("caregiver_id", "CG001") if sess.extracted_data else "CG001"
        initial_data = sess.extracted_data.get("initial", {}) if sess.extracted_data else {}
        processing_method = sess.extracted_data.get("processing_method", "DETERMINISTIC") if sess.extracted_data else "DETERMINISTIC"
        certainty = sess.extracted_data.get("certainty", "CONFIRMED") if sess.extracted_data else "CONFIRMED"
        confidence = sess.extracted_data.get("confidence", "HIGH") if sess.extracted_data else "HIGH"

        # Collect all answers
        answers_dict = {ans.field_name: ans.answer for ans in sess.answers}

        # Build structured observation
        structured = ClarificationEngine.build_structured_observation(
            category=sess.detected_category,
            raw_text=sess.raw_text,
            initial_data=initial_data,
            answers=answers_dict
        )

        # Attach certainty and provenance to structured attributes
        structured["attributes"]["certainty"] = certainty
        structured["attributes"]["confidence"] = confidence
        structured["attributes"]["extraction_method"] = processing_method

        # 1. Generate new Evidence Code (e.g. EV-CG-048, EV-CG-049) without collisions
        ev_count = db.query(Evidence).filter(Evidence.source_type == SourceType.CAREGIVER).count()
        counter = ev_count + 1
        while True:
            candidate_code = f"EV-CG-{counter:03d}"
            if not db.query(Evidence).filter(Evidence.evidence_code == candidate_code).first():
                next_ev_code = candidate_code
                break
            counter += 1

        # 2. Insert Evidence
        new_evidence = Evidence(
            patient_id=patient.id,
            evidence_code=next_ev_code,
            source_type=SourceType.CAREGIVER,
            source_id=caregiver_id,
            observed_at=datetime.now(timezone.utc),
            recorded_at=datetime.now(timezone.utc),
            original_statement=sess.raw_text,
            status=EvidenceStatus.IMMUTABLE
        )
        db.add(new_evidence)
        db.flush()

        # 3. Insert Caregiver Observation
        cg_obs = CaregiverObservation(
            patient_id=patient.id,
            evidence_id=new_evidence.id,
            caregiver_id=caregiver_id,
            category=sess.detected_category,
            observation_text=sess.raw_text,
            attributes=structured.get("attributes", {}),
            observed_at=new_evidence.observed_at,
            information_state=InformationState.OBSERVED
        )
        db.add(cg_obs)

        # 4. Insert general Observation
        gen_obs = Observation(
            patient_id=patient.id,
            evidence_id=new_evidence.id,
            category=sess.detected_category,
            status=InformationState.OBSERVED,
            observed_at=new_evidence.observed_at,
            severity=structured.get("attributes", {}).get("severity"),
            duration=structured.get("attributes", {}).get("duration"),
            onset=structured.get("attributes", {}).get("onset"),
            clarification_required=False
        )
        db.add(gen_obs)

        # 5. Insert Audit Log with provenance
        audit = AuditLog(
            action="CAREGIVER_OBSERVATION_INGESTED",
            entity_type="CaregiverObservation",
            entity_id=str(new_evidence.id),
            details=f"Evidence {next_ev_code} created from session {sess.session_code}. Extraction: {processing_method}. Category: {sess.detected_category}. Certainty: {certainty}."
        )
        db.add(audit)

        # 6. Update Session
        sess.status = SessionStatus.COMPLETED
        sess.completed_at = datetime.now(timezone.utc)
        sess.resulting_evidence_id = new_evidence.id
        db.commit()

        return {
            "session_id": sess.id,
            "status": sess.status,
            "category": sess.detected_category,
            "structured_observation": structured,
            "evidence_id": new_evidence.id,
            "evidence_code": new_evidence.evidence_code,
            "observation_id": cg_obs.id,
            "created_at": new_evidence.created_at
        }
