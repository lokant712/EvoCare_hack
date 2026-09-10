import os

ROOT_DIR = r"c:\Users\lokan\Downloads\journey\sve\EvoCare"
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

def write_file(rel_path, content):
    full_path = os.path.join(BACKEND_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Updated: backend/{rel_path}")

# ==============================================================================
# 1. NEW MODELS: ClarificationSession, ClarificationQuestion, ClarificationAnswer
# ==============================================================================

write_file("app/models/clarification.py", """import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship

from app.core.database import Base

class SessionStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ClarificationSession(Base):
    __tablename__ = "clarification_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_code = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False, index=True)
    raw_text = Column(Text, nullable=False)
    detected_category = Column(String(100), nullable=False, index=True)
    status = Column(SQLEnum(SessionStatus), default=SessionStatus.PENDING, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    resulting_evidence_id = Column(Integer, ForeignKey("evidences.id", ondelete="SET NULL"), nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)

    patient = relationship("Patient")
    resulting_evidence = relationship("Evidence")
    questions = relationship("ClarificationQuestion", back_populates="session", cascade="all, delete-orphan", order_by="ClarificationQuestion.id")
    answers = relationship("ClarificationAnswer", back_populates="session", cascade="all, delete-orphan")

class ClarificationQuestion(Base):
    __tablename__ = "clarification_questions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("clarification_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    field_name = Column(String(100), nullable=False)
    required = Column(Boolean, default=True, nullable=False)
    options = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ClarificationSession", back_populates="questions")
    answers = relationship("ClarificationAnswer", back_populates="question", cascade="all, delete-orphan")

class ClarificationAnswer(Base):
    __tablename__ = "clarification_answers"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("clarification_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("clarification_questions.id", ondelete="CASCADE"), nullable=True, index=True)
    field_name = Column(String(100), nullable=False)
    answer = Column(Text, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    session = relationship("ClarificationSession", back_populates="answers")
    question = relationship("ClarificationQuestion", back_populates="answers")
""")

# Update app/models/__init__.py to include clarification models
write_file("app/models/__init__.py", """from app.models.enums import SourceType, InformationState, EvidenceStatus, ConflictStatus, PageType
from app.models.associations import pattern_evidence_association, conflict_evidence_association, baseline_evidence_association
from app.models.patient import Patient
from app.models.evidence import Evidence
from app.models.observation import Observation
from app.models.caregiver_observation import CaregiverObservation
from app.models.doctor_record import DoctorRecord
from app.models.medication import Medication
from app.models.lab import LabRecord
from app.models.baseline import Baseline
from app.models.pattern import Pattern
from app.models.conflict import Conflict
from app.models.memory_page import MemoryPage
from app.models.audit import AuditLog
from app.models.clarification import SessionStatus, ClarificationSession, ClarificationQuestion, ClarificationAnswer
""")

# ==============================================================================
# 2. SCHEMAS FOR CLARIFICATION & OBSERVATIONS
# ==============================================================================

write_file("app/schemas/clarification.py", """from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.clarification import SessionStatus

class ObservationStartRequest(BaseModel):
    patient_id: Optional[str] = "P001"
    patient_code: Optional[str] = None
    text: str
    caregiver_id: Optional[str] = "CG001"

class ClarificationQuestionResponse(BaseModel):
    id: int
    field_name: str
    question: str
    required: bool
    options: Optional[List[str]] = None

    model_config = ConfigDict(from_attributes=True)

class ObservationStartResponse(BaseModel):
    session_id: int
    session_code: str
    patient_id: int
    patient_code: str
    category: str
    missing_fields: List[str]
    questions: List[ClarificationQuestionResponse]
    status: SessionStatus

class ClarificationAnswerRequest(BaseModel):
    question_id: Optional[int] = None
    field_name: Optional[str] = None
    answer: str

class ClarificationAnswerResponse(BaseModel):
    id: int
    session_id: int
    field_name: str
    answer: str
    answered_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ClarificationSessionResponse(BaseModel):
    id: int
    session_code: str
    patient_id: int
    patient_code: str
    raw_text: str
    detected_category: str
    status: SessionStatus
    questions: List[ClarificationQuestionResponse]
    answers: List[ClarificationAnswerResponse]
    started_at: datetime
    completed_at: Optional[datetime] = None

class ObservationCompleteResponse(BaseModel):
    session_id: int
    status: SessionStatus
    category: str
    structured_observation: Dict[str, Any]
    evidence_id: int
    evidence_code: str
    observation_id: int
    created_at: datetime

class StructuredObservationDetailResponse(BaseModel):
    id: int
    patient_id: int
    evidence_id: int
    evidence_code: str
    source_type: str = "CAREGIVER"
    category: str
    observation_text: str
    attributes: Optional[Dict[str, Any]] = None
    observed_at: datetime
    information_state: str
    clarification_completed: bool
""")

# ==============================================================================
# 3. CLARIFICATION ENGINE
# ==============================================================================

write_file("app/services/clarification_engine.py", """import re
from typing import Dict, Any, List, Tuple

class ClarificationEngine:
    # Category definition & question templates
    QUESTION_TEMPLATES = {
        "dizziness": {
            "severity": {
                "question": "How severe was the dizziness?",
                "options": ["Mild", "Moderate", "Severe", "Not sure"]
            },
            "duration": {
                "question": "How long did the dizziness last?",
                "options": ["A few seconds", "A few minutes", "Several hours", "Unknown / Not sure"]
            },
            "onset": {
                "question": "When or how did the dizziness start?",
                "options": ["After getting out of bed / standing up", "While sitting or resting", "During walking", "Unknown"]
            },
            "trigger": {
                "question": "Was there any noticeable trigger?",
                "options": ["Sudden movement", "Skipped meal", "Heat", "No obvious trigger", "Unknown"]
            },
            "fall_associated": {
                "question": "Did a fall occur during this dizziness episode?",
                "options": ["No fall", "Near-fall (caught)", "Completed fall", "Unknown"]
            }
        },
        "near_fall": {
            "location": {
                "question": "Where did the near-fall occur?",
                "options": ["Near the bathroom", "Bedroom", "Living room / Kitchen", "Outdoors / Stairs", "Unknown"]
            },
            "injury": {
                "question": "Did any injury occur?",
                "options": ["No injury (caught before impact)", "Mild scrape / bruise", "Unknown"]
            },
            "assistance_required": {
                "question": "Was physical assistance needed to catch or stabilize her?",
                "options": ["Yes, caught by caregiver", "Held onto wall/furniture independently", "Unknown"]
            },
            "loss_of_consciousness": {
                "question": "Was there any loss of consciousness?",
                "options": ["No loss of consciousness", "Briefly unresponsive", "Unknown"]
            }
        },
        "fall": {
            "location": {
                "question": "Where did the fall occur?",
                "options": ["Bathroom", "Bedroom", "Living room", "Outside", "Unknown"]
            },
            "injury": {
                "question": "Was there any injury or pain after the fall?",
                "options": ["No apparent injury", "Bruising / Contusion", "Severe pain / Suspected fracture", "Unknown"]
            },
            "assistance_required": {
                "question": "Did she require assistance to stand up?",
                "options": ["Assisted up by caregiver", "Stood up independently", "Paramedics called", "Unknown"]
            }
        },
        "nutrition": {
            "meal": {
                "question": "Which meal was affected?",
                "options": ["Breakfast", "Lunch", "Dinner", "All meals", "Snacks / General"]
            },
            "amount_eaten": {
                "question": "Approximately how much was eaten?",
                "options": ["Only a few bites (<25%)", "About half (50%)", "About three-quarters (75%)", "Finished meal", "Unknown"]
            },
            "appetite_change_duration": {
                "question": "How long has this appetite change lasted?",
                "options": ["Today only", "2-3 days", "Over a week", "Unknown"]
            }
        },
        "cognition": {
            "description": {
                "question": "What specific confusion or memory change was observed?",
                "options": ["Disoriented to time/day", "Asked repetitive questions", "Misplaced items", "Difficulty recognizing familiar context", "Other / General"]
            },
            "duration": {
                "question": "How long did the confusion last?",
                "options": ["Brief moment (few minutes)", "Throughout the evening", "Entire day", "Unknown"]
            },
            "time_of_day": {
                "question": "What time of day did this occur?",
                "options": ["Morning", "Afternoon", "Evening / Dinner time", "Night", "Unknown"]
            }
        },
        "pain": {
            "location": {
                "question": "Where is the pain located?",
                "options": ["Bilateral knees", "Left knee", "Right knee", "Back / Hips", "Other"]
            },
            "severity": {
                "question": "How severe is the discomfort?",
                "options": ["Mild", "Moderate", "Severe", "Exertional discomfort only"]
            },
            "relation_to_exertion": {
                "question": "Is the pain related to physical activity?",
                "options": ["After walking / standing", "At rest", "Constant", "Unknown"]
            }
        },
        "mobility": {
            "support_needed": {
                "question": "What level of support was needed for walking?",
                "options": ["No support (independent)", "Held furniture/walls", "Needed caregiver arm support", "Unable to walk", "Unknown"]
            },
            "activity": {
                "question": "During what activity was unsteadiness observed?",
                "options": ["Getting up from chair", "Walking indoors", "Walking outdoors", "Navigating bathroom"]
            }
        },
        "sleep": {
            "hours_slept": {
                "question": "Approximately how many hours did she sleep?",
                "options": ["Around 7-8 hours (normal)", "4-6 hours (short)", "Less than 4 hours", "Unknown"]
            },
            "night_waking": {
                "question": "Were there nocturnal awakenings?",
                "options": ["No waking", "Woke up 1-2 times", "Woke up 3+ times (fragmented)", "Unknown"]
            }
        },
        "behavior": {
            "mood_description": {
                "question": "How would you describe her demeanor or mood?",
                "options": ["Cheerful / Social", "Quiet / Withdrawn", "Frustrated", "Agitated", "Normal"]
            }
        },
        "medication_adherence": {
            "taken_on_time": {
                "question": "Were the scheduled medications taken?",
                "options": ["Taken on time", "Taken with delay / reminder", "Missed dose", "Organized for the week"]
            },
            "assistance_provided": {
                "question": "Was caregiver assistance provided?",
                "options": ["Yes, administered / reminded by caregiver", "Taken independently", "Pillbox organized"]
            }
        }
    }

    REQUIRED_FIELDS = {
        "dizziness": ["severity", "duration", "onset"],
        "near_fall": ["location", "injury", "assistance_required"],
        "fall": ["location", "injury", "assistance_required"],
        "nutrition": ["meal", "amount_eaten"],
        "cognition": ["description", "duration"],
        "pain": ["location", "severity"],
        "mobility": ["support_needed", "activity"],
        "sleep": ["hours_slept", "night_waking"],
        "behavior": ["mood_description"],
        "medication_adherence": ["taken_on_time", "assistance_provided"]
    }

    @classmethod
    def detect_category(cls, text: str) -> str:
        t = text.lower()
        if "almost fell" in t or "nearly fell" in t or "slipped but caught" in t or "lost balance but caught" in t:
            return "near_fall"
        elif re.search(r"\b(fell|fall|collapsed|hit the floor)\b", t):
            return "fall"
        elif re.search(r"\b(dizzy|dizziness|giddy|lightheaded|spinning|vertigo)\b", t):
            return "dizziness"
        elif re.search(r"\b(eat|ate|lunch|dinner|breakfast|food|appetite|bites|meal|intake|hungry)\b", t):
            return "nutrition"
        elif re.search(r"\b(confused|confusion|forgot|forget|remember|memory|disoriented|repeating)\b", t):
            return "cognition"
        elif re.search(r"\b(hurt|pain|ache|aching|sore|discomfort|knees|joint)\b", t):
            return "pain"
        elif re.search(r"\b(walk|walking|unsteady|stumble|limp|support|gait|arm|chair|table)\b", t):
            return "mobility"
        elif re.search(r"\b(sleep|slept|woke|waking|insomnia|night|bedtime)\b", t):
            return "sleep"
        elif re.search(r"\b(medicine|medicines|pills|dose|tablet|medication|reminded|pillbox)\b", t):
            return "medication_adherence"
        elif re.search(r"\b(mood|frustrated|quiet|laughing|crying|temper|demure|social)\b", t):
            return "behavior"
        else:
            return "mobility"

    @classmethod
    def extract_initial_fields(cls, category: str, text: str) -> Dict[str, Any]:
        t = text.lower()
        extracted = {}

        # Dizziness heuristics
        if category == "dizziness":
            if "mild" in t or "a little" in t:
                extracted["severity"] = "Mild"
            elif "severe" in t or "badly" in t:
                extracted["severity"] = "Severe"
            if "getting out of bed" in t or "standing" in t or "stood up" in t:
                extracted["onset"] = "After getting out of bed / standing up"
            if "seconds" in t or "few seconds" in t:
                extracted["duration"] = "A few seconds"
            elif "minutes" in t:
                extracted["duration"] = "A few minutes"

        # Near-fall heuristics
        elif category == "near_fall":
            extracted["event_type"] = "NEAR_FALL"
            extracted["loss_of_consciousness"] = "No loss of consciousness"
            if "bathroom" in t:
                extracted["location"] = "Near the bathroom"
            if "caught" in t:
                extracted["assistance_required"] = "Yes, caught by caregiver"
                extracted["injury"] = "No injury (caught before impact)"

        # Nutrition heuristics
        elif category == "nutrition":
            if "lunch" in t:
                extracted["meal"] = "Lunch"
            elif "dinner" in t:
                extracted["meal"] = "Dinner"
            elif "breakfast" in t:
                extracted["meal"] = "Breakfast"
            if "half" in t:
                extracted["amount_eaten"] = "About half (50%)"
            elif "few bites" in t or "hardly" in t or "didn't eat much" in t:
                extracted["amount_eaten"] = "Only a few bites (<25%)"
            elif "three quarters" in t or "most" in t:
                extracted["amount_eaten"] = "About three-quarters (75%)"

        # Cognition heuristics
        elif category == "cognition":
            if "evening" in t or "dinner" in t:
                extracted["time_of_day"] = "Evening / Dinner time"
            elif "morning" in t:
                extracted["time_of_day"] = "Morning"
            if "day" in t and ("what day" in t or "which day" in t):
                extracted["description"] = "Disoriented to time/day"
            elif "question twice" in t or "repeating" in t:
                extracted["description"] = "Asked repetitive questions"
            elif "glasses" in t or "keys" in t:
                extracted["description"] = "Misplaced items"

        # Pain heuristics
        elif category == "pain":
            if "knees" in t or "knee" in t:
                extracted["location"] = "Bilateral knees"
            if "mild" in t or "a little" in t:
                extracted["severity"] = "Mild"
            if "after walking" in t or "outside" in t:
                extracted["relation_to_exertion"] = "After walking / standing"

        return extracted

    @classmethod
    def get_missing_fields(cls, category: str, extracted: Dict[str, Any]) -> List[str]:
        req = cls.REQUIRED_FIELDS.get(category, [])
        return [f for f in req if f not in extracted or not extracted[f]]

    @classmethod
    def generate_questions(cls, category: str, missing_fields: List[str]) -> List[Dict[str, Any]]:
        templates = cls.QUESTION_TEMPLATES.get(category, {})
        questions = []
        for field in missing_fields:
            if field in templates:
                t = templates[field]
                questions.append({
                    "field_name": field,
                    "question": t["question"],
                    "required": True,
                    "options": t.get("options", [])
                })
            else:
                questions.append({
                    "field_name": field,
                    "question": f"Please specify the {field.replace('_', ' ')}:",
                    "required": True,
                    "options": ["Not sure / Unknown"]
                })
        return questions

    @classmethod
    def build_structured_observation(cls, category: str, raw_text: str, initial_data: Dict[str, Any], answers: Dict[str, Any]) -> Dict[str, Any]:
        merged = {**initial_data, **answers}
        
        # Clean up any missing required fields with explicit UNKNOWN
        req = cls.REQUIRED_FIELDS.get(category, [])
        for f in req:
            if f not in merged or not merged[f]:
                merged[f] = "UNKNOWN"

        structured = {
            "category": category,
            "raw_statement": raw_text,
            "attributes": merged,
            "clarification_complete": True,
            "clinical_diagnoses_inferred": False  # Enforcing safety invariant
        }

        # Add domain specific non-diagnostic interpretations
        if category == "near_fall":
            structured["classification"] = "NEAR_FALL"
            structured["ground_impact"] = False
        elif category == "dizziness":
            structured["etiology"] = "UNKNOWN (Requires Clinician Evaluation)"
        elif category == "cognition":
            structured["dementia_diagnosed"] = False

        return structured
""")

# ==============================================================================
# 4. OBSERVATION PIPELINE SERVICE
# ==============================================================================

write_file("app/services/observation_pipeline_service.py", """import uuid
from datetime import datetime
from typing import Dict, Any, List
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

class ObservationPipelineService:
    @staticmethod
    def start_session(db: Session, patient_id_or_code: Any, raw_text: str, caregiver_id: str = "CG001") -> Dict[str, Any]:
        # 1. Resolve Patient
        if isinstance(patient_id_or_code, int) or (isinstance(patient_id_or_code, str) and patient_id_or_code.isdigit()):
            patient = db.query(Patient).filter(Patient.id == int(patient_id_or_code)).first()
        else:
            patient = db.query(Patient).filter(Patient.patient_code == str(patient_id_or_code)).first()

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Patient '{patient_id_or_code}' not found"
            )

        # 2. Clarification Engine Category & Field Extraction
        category = ClarificationEngine.detect_category(raw_text)
        initial_extracted = ClarificationEngine.extract_initial_fields(category, raw_text)
        missing_fields = ClarificationEngine.get_missing_fields(category, initial_extracted)
        question_templates = ClarificationEngine.generate_questions(category, missing_fields)

        # 3. Create Session
        session_code = f"SESS-{uuid.uuid4().hex[:8].upper()}"
        sess = ClarificationSession(
            session_code=session_code,
            patient_id=patient.id,
            raw_text=raw_text,
            detected_category=category,
            status=SessionStatus.PENDING if missing_fields else SessionStatus.IN_PROGRESS,
            extracted_data={"initial": initial_extracted, "caregiver_id": caregiver_id},
            started_at=datetime.utcnow()
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
            "status": sess.status
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
            existing_ans.answered_at = datetime.utcnow()
            ans = existing_ans
        else:
            ans = ClarificationAnswer(
                session_id=session_id,
                question_id=question_id,
                field_name=target_field,
                answer=answer_text,
                answered_at=datetime.utcnow()
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

        # Collect all answers
        answers_dict = {ans.field_name: ans.answer for ans in sess.answers}

        # Build structured observation
        structured = ClarificationEngine.build_structured_observation(
            category=sess.detected_category,
            raw_text=sess.raw_text,
            initial_data=initial_data,
            answers=answers_dict
        )

        # 1. Generate new Evidence Code (e.g. EV-CG-048, EV-CG-049)
        ev_count = db.query(Evidence).filter(Evidence.source_type == SourceType.CAREGIVER).count()
        next_ev_code = f"EV-CG-{ev_count + 1:03d}"

        # 2. Insert Evidence
        new_evidence = Evidence(
            patient_id=patient.id,
            evidence_code=next_ev_code,
            source_type=SourceType.CAREGIVER,
            source_id=caregiver_id,
            observed_at=datetime.utcnow(),
            recorded_at=datetime.utcnow(),
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

        # 5. Insert Audit Log
        audit = AuditLog(
            action="CAREGIVER_OBSERVATION_INGESTED",
            entity_type="CaregiverObservation",
            entity_id=str(new_evidence.id),
            details=f"Evidence {next_ev_code} created from session {sess.session_code}. Category: {sess.detected_category}."
        )
        db.add(audit)

        # 6. Update Session
        sess.status = SessionStatus.COMPLETED
        sess.completed_at = datetime.utcnow()
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
""")

# ==============================================================================
# 5. NEW ROUTER: app/routers/clarification.py & Update app/main.py
# ==============================================================================

write_file("app/routers/clarification.py", """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.caregiver_observation import CaregiverObservation
from app.schemas.clarification import (
    ObservationStartRequest,
    ObservationStartResponse,
    ClarificationQuestionResponse,
    ClarificationAnswerRequest,
    ClarificationAnswerResponse,
    ClarificationSessionResponse,
    ObservationCompleteResponse,
    StructuredObservationDetailResponse
)
from app.services.observation_pipeline_service import ObservationPipelineService

router = APIRouter(tags=["Caregiver Observation Intelligence & Clarification"])

@router.post("/observations/start", response_model=ObservationStartResponse, status_code=status.HTTP_201_CREATED)
def start_observation_pipeline(request: ObservationStartRequest, db: Session = Depends(get_db)):
    target_patient = request.patient_code or request.patient_id or "P001"
    result = ObservationPipelineService.start_session(
        db=db,
        patient_id_or_code=target_patient,
        raw_text=request.text,
        caregiver_id=request.caregiver_id or "CG001"
    )
    return result

@router.get("/clarification/{session_id}", response_model=ClarificationSessionResponse)
def get_clarification_session(session_id: int, db: Session = Depends(get_db)):
    sess = ObservationPipelineService.get_session(db, session_id)
    return ClarificationSessionResponse(
        id=sess.id,
        session_code=sess.session_code,
        patient_id=sess.patient_id,
        patient_code=sess.patient.patient_code if sess.patient else "P001",
        raw_text=sess.raw_text,
        detected_category=sess.detected_category,
        status=sess.status,
        questions=[ClarificationQuestionResponse.model_validate(q) for q in sess.questions],
        answers=[ClarificationAnswerResponse.model_validate(a) for a in sess.answers],
        started_at=sess.started_at,
        completed_at=sess.completed_at
    )

@router.post("/clarification/{session_id}/answer", response_model=ClarificationAnswerResponse)
def submit_clarification_answer(
    session_id: int,
    payload: ClarificationAnswerRequest,
    db: Session = Depends(get_db)
):
    ans = ObservationPipelineService.answer_question(
        db=db,
        session_id=session_id,
        question_id=payload.question_id,
        field_name=payload.field_name,
        answer_text=payload.answer
    )
    return ans

@router.post("/clarification/{session_id}/complete", response_model=ObservationCompleteResponse)
def complete_clarification_pipeline(session_id: int, db: Session = Depends(get_db)):
    return ObservationPipelineService.complete_session(db, session_id)

@router.get("/observations/{observation_id}", response_model=StructuredObservationDetailResponse)
def get_structured_observation(observation_id: int, db: Session = Depends(get_db)):
    obs = db.query(CaregiverObservation).filter(CaregiverObservation.id == observation_id).first()
    if not obs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caregiver observation with id {observation_id} not found"
        )
    return StructuredObservationDetailResponse(
        id=obs.id,
        patient_id=obs.patient_id,
        evidence_id=obs.evidence_id,
        evidence_code=obs.evidence.evidence_code if obs.evidence else "UNKNOWN",
        source_type="CAREGIVER",
        category=obs.category,
        observation_text=obs.observation_text,
        attributes=obs.attributes,
        observed_at=obs.observed_at,
        information_state=obs.information_state.value,
        clarification_completed=True
    )
""")

# Update app/main.py
write_file("app/main.py", """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Load all models for metadata

# Initialize database schema
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Longitudinal Memory System & Clinical Intelligence API for Elderly Healthcare",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

# Include routers
from app.routers import (
    patients,
    evidence,
    caregiver,
    clinical,
    medications,
    labs,
    memory,
    timeline,
    observations,
    clarification
)

app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(caregiver.router, prefix=settings.API_V1_STR)
app.include_router(clinical.router, prefix=settings.API_V1_STR)
app.include_router(medications.router, prefix=settings.API_V1_STR)
app.include_router(labs.router, prefix=settings.API_V1_STR)
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(timeline.router, prefix=settings.API_V1_STR)
app.include_router(observations.router, prefix=settings.API_V1_STR)
app.include_router(clarification.router, prefix=settings.API_V1_STR)
""")

print("Phase 3 pipeline files written successfully.")
