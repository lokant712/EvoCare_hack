import json
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from app.services.llm.schemas import (
    ParsedCaregiverObservation,
    ObservationCategory,
    EventType,
    ConfidenceLevel,
    CertaintyState,
    LLMStatus,
    ProcessingMethod,
)
from app.services.llm.validator import ObservationValidator
from app.services.llm.safety_validator import SafetyValidator

class LLMResult(BaseModel):
    status: LLMStatus
    parsed_observation: Optional[ParsedCaregiverObservation] = None
    raw_response: Optional[str] = None
    error_message: Optional[str] = None
    processing_method: ProcessingMethod = ProcessingMethod.LLM_ASSISTED
    safety_violations: List[str] = []

class LLMProvider(ABC):
    @abstractmethod
    def extract_observation(self, text: str, patient_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        """
        Extract a structured observation from raw caregiver text.
        Must return an LLMResult.
        """
        pass

    @abstractmethod
    def generate_clinical_reasoning(self, question: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate structured clinical reasoning from question and structured patient context.
        Must return a dictionary matching clinical reasoning schema.
        """
        pass

class MockLLMProvider(LLMProvider):
    """
    Mock LLM Provider for unit testing and offline demo execution.
    Can be configured with fixed responses or default realistic behavioral extraction.
    """
    def __init__(
        self,
        fixed_response: Optional[str] = None,
        fixed_reasoning_response: Optional[Dict[str, Any]] = None,
        force_status: Optional[LLMStatus] = None,
        error_message: Optional[str] = None
    ):
        self.fixed_response = fixed_response
        self.fixed_reasoning_response = fixed_reasoning_response
        self.force_status = force_status
        self.error_message = error_message

    def extract_observation(self, text: str, patient_context: Optional[Dict[str, Any]] = None) -> LLMResult:
        if self.force_status == LLMStatus.LLM_UNAVAILABLE:
            return LLMResult(
                status=LLMStatus.LLM_UNAVAILABLE,
                error_message=self.error_message or "Anthropic API key is not configured or LLM is disabled",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        if self.force_status == LLMStatus.ERROR:
            return LLMResult(
                status=LLMStatus.ERROR,
                error_message=self.error_message or "Simulated provider error",
                processing_method=ProcessingMethod.LLM_FALLBACK
            )

        # If a fixed string is provided, validate it
        if self.fixed_response is not None:
            raw_resp = self.fixed_response
            is_valid, parsed_obs, err = ObservationValidator.validate_raw_response(raw_resp, text)
            if not is_valid:
                return LLMResult(
                    status=LLMStatus.VALIDATION_FAILED,
                    raw_response=raw_resp,
                    error_message=err,
                    processing_method=ProcessingMethod.LLM_FALLBACK
                )
            
            is_safe, violations = SafetyValidator.validate_safety(parsed_obs, text)
            if not is_safe:
                return LLMResult(
                    status=LLMStatus.SAFETY_REJECTED,
                    parsed_observation=parsed_obs,
                    raw_response=raw_resp,
                    safety_violations=violations,
                    error_message=f"Safety check rejected LLM output: {'; '.join(violations)}",
                    processing_method=ProcessingMethod.LLM_FALLBACK
                )

            return LLMResult(
                status=LLMStatus.SUCCESS,
                parsed_observation=parsed_obs,
                raw_response=raw_resp,
                processing_method=ProcessingMethod.LLM_ASSISTED
            )

        # Generate realistic default mock output for scenario evaluation
        t = text.lower()
        category = ObservationCategory.OTHER
        event_type = EventType.GENERAL_OBSERVATION
        severity = "UNKNOWN"
        duration = "UNKNOWN"
        onset = "UNKNOWN"
        context = "UNKNOWN"
        clarification_fields = []
        requires_clarification = True
        ground_impact = False
        certainty = CertaintyState.CONFIRMED
        confidence = ConfidenceLevel.HIGH
        negations = []
        associated = {}

        if "i think" in t or "maybe" in t or "perhaps" in t or "seems like" in t:
            certainty = CertaintyState.UNCERTAIN
            confidence = ConfidenceLevel.LOW

        if "almost fell" in t or "nearly fell" in t:
            category = ObservationCategory.NEAR_FALL
            event_type = EventType.NEAR_FALL
            ground_impact = False
            clarification_fields = ["location", "injury", "assistance_required"]
            if "bathroom" in t:
                context = "Near the bathroom"
                associated["location"] = "Near the bathroom"
                clarification_fields.remove("location")
        elif "fell" in t and "not fall" not in t and "didn't fall" not in t:
            category = ObservationCategory.FALL
            event_type = EventType.FALL
            ground_impact = True
            clarification_fields = ["location", "injury", "assistance_required"]
            if "bathroom" in t:
                context = "Bathroom"
                associated["location"] = "Bathroom"
                clarification_fields.remove("location")
        elif "dizzy" in t or "dizziness" in t:
            category = ObservationCategory.DIZZINESS
            event_type = EventType.DIZZINESS_EPISODE
            clarification_fields = ["severity", "duration", "onset"]
            if "severe" in t:
                severity = "Severe"
                clarification_fields.remove("severity")
            elif "mild" in t:
                severity = "Mild"
                clarification_fields.remove("severity")
            if "10 minutes" in t:
                duration = "approximately 10 minutes"
                clarification_fields.remove("duration")
            elif "few seconds" in t:
                duration = "A few seconds"
                clarification_fields.remove("duration")
            if "getting out of bed" in t or "standing" in t:
                onset = "getting out of bed / standing up"
                clarification_fields.remove("onset")
        elif "confused" in t or "forget" in t or "glasses" in t:
            category = ObservationCategory.COGNITION
            event_type = EventType.CONFUSION_EPISODE
            clarification_fields = ["description", "duration"]
            associated["description"] = "Confusion / Disorientation observed"
        elif "eat" in t or "dinner" in t or "lunch" in t or "breakfast" in t or "appetite" in t:
            category = ObservationCategory.NUTRITION
            event_type = EventType.APPETITE_CHANGE
            clarification_fields = ["meal", "amount_eaten"]
            if "dinner" in t:
                associated["meal"] = "Dinner"
                clarification_fields.remove("meal")
            elif "lunch" in t:
                associated["meal"] = "Lunch"
                clarification_fields.remove("meal")
            if "didn't eat much" in t or "not much" in t:
                associated["amount_eaten"] = "reduced / limited"
        elif "medicine" in t or "pills" in t or "dose" in t:
            category = ObservationCategory.MEDICATION_ADHERENCE
            event_type = EventType.MEDICATION_EVENT
            clarification_fields = ["taken_on_time", "assistance_provided"]
        elif "weak" in t:
            category = ObservationCategory.OTHER
            event_type = EventType.GENERAL_OBSERVATION
            clarification_fields = ["support_needed", "activity"]
            associated["symptom"] = "Weakness reported"

        requires_clarification = len(clarification_fields) > 0

        parsed_obs = ParsedCaregiverObservation(
            category=category,
            event_type=event_type,
            severity=severity,
            duration=duration,
            onset=onset,
            context=context,
            associated_details=associated,
            negations=negations,
            confidence=confidence,
            certainty=certainty,
            unknown_fields=[f for f in ["severity", "duration", "frequency", "onset"] if f in clarification_fields],
            requires_clarification=requires_clarification,
            clarification_fields=clarification_fields,
            etiology="UNKNOWN",
            diagnosis=None,
            dementia_diagnosed=False,
            clinical_diagnoses_inferred=False,
            ground_impact=ground_impact,
            raw_statement=text
        )

        return LLMResult(
            status=LLMStatus.SUCCESS,
            parsed_observation=parsed_obs,
            raw_response=parsed_obs.model_dump_json(),
            processing_method=ProcessingMethod.LLM_ASSISTED
        )

    def generate_clinical_reasoning(self, question: str, patient_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deterministic mock reasoning generator supporting all 4 standard clinical demo scenarios
        and custom test inputs.
        """
        if self.fixed_reasoning_response is not None:
            return self.fixed_reasoning_response

        q = question.lower()

        # Scenario: Previous Doctor Consultations / Clinic Reviews
        if any(w in q for w in ["doctor", "consult", "consulted", "consultation", "physician", "specialist", "clinic visit", "who examined", "who treated", "encounters"]):
            return {
                "considerations": [
                    {
                        "title": "Documented Outpatient Clinical Reviews & Physician Encounters",
                        "category": "Clinical Consultations",
                        "description": "Patient has 5 documented clinician consultations (EV-DR-001 through EV-DR-005) for ongoing management of Type 2 Diabetes, Hypertension, Hyperlipidemia, and Knee Osteoarthritis. Consultations recorded stable glycemic control (HbA1c 7.1% - 7.4%), blood pressure maintenance (BP 132/82 mmHg), independent indoor ambulation, and no acute neurological deficits.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-DR-001",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-06-12",
                                "original_statement": "Routine geriatric clinical review. Assessed for Type 2 Diabetes Mellitus, Hypertension, Hyperlipidemia, and bilateral Knee Osteoarthritis. Physical examination reveals independent mobility and steady gait without assistive devices."
                            },
                            {
                                "evidence_id": "EV-DR-002",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-07-08",
                                "original_statement": "Bimonthly follow-up visit. Chronic medical conditions remain reasonably stable. Diabetes monitoring continued with recent HbA1c 7.1%. Ambulation remains fully independent."
                            },
                            {
                                "evidence_id": "EV-DR-003",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-08-01",
                                "original_statement": "Routine clinical follow-up. Vital signs: BP 132/82 mmHg, Pulse 74 bpm. Patient remains independently mobile around her residence and community. Orientation to time, place, and person intact."
                            },
                            {
                                "evidence_id": "EV-DR-005",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Routine clinical review. Patient ambulates independently into consultation room with steady pace. No acute focal neurological deficits. Glycemic control stable (HbA1c 7.4%)."
                            }
                        ],
                        "contradicting_evidence": [
                            "No contradictory clinical records found. Outpatient physician assessments consistently report independent ambulation and stable vitals."
                        ],
                        "missing_information": [
                            "Annual ophthalmology diabetic eye examination report",
                            "Formal physical therapy gait & balance assessment note"
                        ],
                        "evidence_strength": "STRONG",
                        "reasoning": "Derived directly from 5 clinician-confirmed consultation records in the longitudinal health memory (EV-DR-001, EV-DR-002, EV-DR-003, EV-DR-005).",
                        "uncertainty": "Clinic encounters confirm stability during structured evaluations; day-to-day balance fluctuations are tracked via caregiver observations.",
                        "references": ["EV-DR-001", "EV-DR-002", "EV-DR-003", "EV-DR-005"]
                    }
                ],
                "missing_information": [
                    "Recent ophthalmology diabetic eye evaluation",
                    "Comprehensive metabolic panel beyond routine HbA1c"
                ],
                "red_flags": [
                    "Missed follow-up appointments or unmonitored chronic disease management warrant clinical review."
                ],
                "relevant_changes": [
                    "Clinical consults indicate stable outpatient management (Metformin 500mg BID, Amlodipine 5mg OD, Atorvastatin 10mg ON, Paracetamol PRN)."
                ],
                "limitations": [
                    "Records represent scheduled outpatient appointments; transient domestic symptoms rely on caregiver logging."
                ]
            }

        # Scenario 3: Dementia question
        if "dementia" in q or "alzheimer" in q:
            return {
                "considerations": [
                    {
                        "title": "Caregiver-Reported Episodic Disorientation",
                        "category": "Cognitive Observation",
                        "description": "Caregiver has documented isolated episodes of forgetfulness/confusion at home, but formal cognitive assessment in clinic was intact.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-CG-040",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-08-30",
                                "original_statement": "Patient seemed confused about what day of the week it was this morning."
                            }
                        ],
                        "contradicting_evidence": [
                            "Formal clinic assessment (DOC-001) documented: Alert, oriented x 3, normal mini-cognitive screen.",
                            "No clinician-confirmed dementia diagnosis exists in the medical record."
                        ],
                        "missing_information": [
                            "Formal neuropsychological evaluation / MoCA or MMSE score",
                            "Screening for acute reversible causes (UTI, electrolyte disturbance, medication anticholinergic burden)"
                        ],
                        "evidence_strength": "LIMITED",
                        "reasoning": "The available record contains caregiver-reported episodes of confusion/forgetfulness, but does not establish a dementia diagnosis. Further formal clinical assessment would be required.",
                        "uncertainty": "Episodic caregiver confusion does not meet criteria for neurocognitive disorder without formal objective evaluation.",
                        "references": ["EV-CG-040", "EV-DR-001"]
                    }
                ],
                "missing_information": [
                    "Standardized cognitive testing (MoCA/MMSE)",
                    "Urinalysis / Metabolic panel to rule out delirium or reversible encephalopathy"
                ],
                "red_flags": [
                    "Rapid acute cognitive decline, hallucinations, or sudden behavioral changes warrant immediate medical evaluation."
                ],
                "relevant_changes": [
                    "Cognition: Baseline intact -> intermittent caregiver-observed confusion (clinic exam remains alert and oriented x3)."
                ],
                "limitations": [
                    "Caregiver observations of confusion are subjective and unstandardized."
                ]
            }

        # Scenario 5: Patient Medical History / Longitudinal Overview
        if any(w in q for w in ["history", "medical history", "overview", "background", "profile", "summary"]):
            return {
                "considerations": [
                    {
                        "title": "Documented Medical History & Chronic Disease Profile",
                        "category": "Medical History",
                        "description": "78-year-old female with long-term managed Type 2 Diabetes Mellitus (~2014, Metformin 500mg BID), Essential Hypertension (~2016, Amlodipine 5mg OD), Hyperlipidemia (Atorvastatin 10mg ON), and Bilateral Knee Osteoarthritis (Kellgren-Lawrence Grade II, PRN Paracetamol). Documented independent functional baseline in activities of daily living.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-DR-001",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-06-12",
                                "original_statement": "Diagnosed Type 2 Diabetes, Hypertension, Hyperlipidemia, bilateral knee OA. Routine clinical follow-up."
                            },
                            {
                                "evidence_id": "EV-DR-005",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Follow-up visit: BP 132/82, HbA1c 7.4%. Patient ambulatory, oriented x3."
                            },
                            {
                                "evidence_id": "EV-MR-001",
                                "source_type": "MEDICAL_RECORD",
                                "observed_at": "2026-01-10",
                                "original_statement": "Longitudinal summary: 77-year-old female with T2DM, HTN, DLP, OA knees. Stable control."
                            },
                            {
                                "evidence_id": "EV-PAT-001",
                                "source_type": "PATIENT-REPORTED",
                                "observed_at": "2026-01-15",
                                "original_statement": "Historical accidental slip at home in January 2026 without fracture or hospitalization."
                            }
                        ],
                        "contradicting_evidence": [
                            "No contradictory medical records identified. Medical history is consistent across all clinical encounters."
                        ],
                        "missing_information": [
                            "Exact radiographic progression date for knee osteoarthritis",
                            "Recent comprehensive metabolic panel beyond HbA1c"
                        ],
                        "evidence_strength": "STRONG",
                        "reasoning": "Derived directly from clinician-confirmed medical assessments (EV-DR-001, EV-DR-005) and longitudinal wiki records ([[Clinical/Medical History]], [[Patient Overview]]).",
                        "uncertainty": "Chronic conditions are confirmed and stable. Historical slip resolved with no sequelae.",
                        "references": ["EV-DR-001", "EV-DR-005", "EV-MR-001", "EV-PAT-001"]
                    }
                ],
                "missing_information": [
                    "Recent comprehensive metabolic panel (electrolytes, renal function)",
                    "Current orthostatic vital sign recordings"
                ],
                "red_flags": [
                    "Acute chest discomfort, focal neurological changes, or sudden functional decompensation warrant urgent evaluation."
                ],
                "relevant_changes": [
                    "Medical history remains stable; recent caregiver observations document domestic mobility unsteadiness and episodic dizziness in Sep 2026."
                ],
                "limitations": [
                    "Historical medical records reflect periodic outpatient visits; continuous home trajectory relies on caregiver logging."
                ]
            }

        # Scenario 6: Caregiver / Caretaker notes for past week
        if any(w in q for w in ["caretaker", "caregiver", "notes", "past week", "recent observations"]):
            return {
                "considerations": [
                    {
                        "title": "Recent Caregiver Observations & Home Trajectory (Past Week)",
                        "category": "Caregiver Observations",
                        "description": "Caregivers logged multiple home observations including morning dizziness upon rising, bilateral knee pain after walking in the garden, temporary appetite reduction (eating half lunch), transient evening confusion, and a near-fall on 2026-09-06 where she was caught before ground impact.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-CG-045",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-01",
                                "original_statement": "Stumbled near bathroom door; caught by caregiver before hitting floor. No ground impact, no injury."
                            },
                            {
                                "evidence_id": "EV-CG-041",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-03",
                                "original_statement": "Patient felt dizzy after getting out of bed; resolved after sitting back down for a few minutes."
                            },
                            {
                                "evidence_id": "EV-CG-046",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Walked normally inside the house today without holding furniture."
                            },
                            {
                                "evidence_id": "EV-CG-040",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-08-30",
                                "original_statement": "Patient seemed confused about what day of the week it was this morning."
                            }
                        ],
                        "contradicting_evidence": [
                            "Independent clinic exam on 2026-09-02 (EV-DR-005) showed steady unassisted gait, contrasting with domestic balance fluctuations."
                        ],
                        "missing_information": [
                            "Orthostatic vital signs during dizzy spells",
                            "Formal home environmental safety assessment"
                        ],
                        "evidence_strength": "MODERATE",
                        "reasoning": "Caregiver observations capture daily functional variability at home that outpatient clinic visits cannot detect.",
                        "uncertainty": "Dizziness etiology is unconfirmed; near-fall had zero ground impact and zero trauma.",
                        "references": ["EV-CG-045", "EV-CG-041", "EV-CG-046", "EV-CG-040"]
                    }
                ],
                "missing_information": [
                    "Orthostatic blood pressure & pulse",
                    "Timing of Amlodipine administration relative to morning symptoms"
                ],
                "red_flags": [
                    "Near-fall event (EV-CG-045) and episodic dizziness warrant fall risk review."
                ],
                "relevant_changes": [
                    "Longitudinal shift: Independent baseline -> intermittent assistance needed -> near-fall on Sep 06 (no injury) -> spontaneous recovery."
                ],
                "limitations": [
                    "Caregiver observations rely on subjective family reports without calibrated instrumentation."
                ]
            }

        # Scenario 4: Mobility worsening question
        if "mobility" in q and ("worsen" in q or "change" in q or "decline" in q or "how has" in q):
            return {
                "considerations": [
                    {
                        "title": "Fluctuating Mobility with Intermittent Support Need & Near-Fall",
                        "category": "Mobility Trajectory",
                        "description": "Longitudinal record reflects episodic balance decline and a near-fall event, followed by documented spontaneous improvement in indoor ambulation.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-CG-045",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-01",
                                "original_statement": "Stumbled near bathroom door; caught by caregiver before hitting floor. No ground impact, no injury."
                            },
                            {
                                "evidence_id": "EV-CG-046",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Walked normally inside the house today without holding furniture."
                            }
                        ],
                        "contradicting_evidence": [
                            "Later caregiver observation (EV-CG-046) documents recovery of unassisted indoor walking.",
                            "Clinic exam (DOC-001) observed steady unassisted gait on flat surfaces."
                        ],
                        "missing_information": [
                            "Formal physical therapy / timed up and go (TUG) assessment",
                            "Environmental home hazard evaluation"
                        ],
                        "evidence_strength": "MODERATE",
                        "reasoning": "Mobility has shown recent fluctuation, including periods requiring support and a near-fall, followed by later improvement. The trajectory is fluctuating rather than permanent linear decline.",
                        "uncertainty": "Caregiver reports describe episodic unsteadiness; baseline independence remains partially preserved indoors.",
                        "references": ["EV-CG-045", "EV-CG-046"]
                    }
                ],
                "missing_information": [
                    "Objective gait speed / Timed Up and Go (TUG) testing",
                    "Continuous activity or sensor tracking data"
                ],
                "red_flags": [
                    "Inability to bear weight, new asymmetry/weakness, or recurrent ground-level falls warrant urgent physical examination."
                ],
                "relevant_changes": [
                    "Mobility: Baseline independent -> outdoor support needed -> near-fall on 2026-09-01 -> indoor walking improved on 2026-09-02."
                ],
                "limitations": [
                    "Home observations rely on caregiver witness availability and subjective difficulty estimation."
                ]
            }

        # Scenario: Sleep / Night Waking / Nocturia
        if any(w in q for w in ["sleep", "insomnia", "nocturia", "night", "waking", "rest", "tired"]):
            return {
                "considerations": [
                    {
                        "title": "Documented Sleep Architecture & Nocturnal Disturbance Patterns",
                        "category": "Sleep & Circadian Profile",
                        "description": "Longitudinal records and caregiver sleep logs indicate fragmented sleep pattern averaging 5-6 hours total, with 1-2 nocturia episodes per night. Patient baseline notes benign sleep fragmentation without reported daytime somnolence, though nocturnal bathroom trips increase nighttime fall vulnerability.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-CG-041",
                                "source_type": "CAREGIVER-REPORTED",
                                "observed_at": "2026-09-03",
                                "original_statement": "Patient felt dizzy after getting out of bed; resolved after sitting back down for a few minutes."
                            },
                            {
                                "evidence_id": "EV-DR-003",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-08-01",
                                "original_statement": "Routine clinical follow-up. Chronic conditions stable. No major functional decline documented."
                            }
                        ],
                        "contradicting_evidence": [
                            "No documented primary sleep disorder or sedative hypnotic prescription in the medical record."
                        ],
                        "missing_information": [
                            "Nighttime hallway lighting and bathroom path illumination check",
                            "Fluid intake distribution in evening hours"
                        ],
                        "evidence_strength": "MODERATE",
                        "reasoning": "Derived from baseline clinical sleep logs ([[Caregiver/Sleep]], [[Derived/Baseline]]) and observed morning postural transitions.",
                        "uncertainty": "Nocturia frequency is stable; nocturnal mobilization poses primary risk for balance instability.",
                        "references": ["EV-CG-041", "EV-DR-003"]
                    }
                ],
                "missing_information": [
                    "Evening fluid restriction adherence",
                    "Overnight pulse oximetry or sleep apnea screening if snoring develops"
                ],
                "red_flags": [
                    "Nocturnal dyspnea, orthopnea, or sudden confusion during nighttime waking warrant prompt cardiopulmonary evaluation."
                ],
                "relevant_changes": [
                    "Sleep logs reflect stable 5-6 hours sleep with night waking managed with bedside nightlight."
                ],
                "limitations": [
                    "Home sleep estimates are derived from self-report and caregiver morning check-ins."
                ]
            }

        # Scenario: Pain / Knee Joint Osteoarthritis
        if any(w in q for w in ["pain", "knee", "joint", "osteoarthritis", "ache", "stiffness", "arthritis"]):
            return {
                "considerations": [
                    {
                        "title": "Bilateral Knee Osteoarthritis & Activity-Related Joint Pain Trajectory",
                        "category": "Musculoskeletal & Pain",
                        "description": "Patient has confirmed Kellgren-Lawrence Grade II bilateral Knee Osteoarthritis (EV-DR-001). Caregiver logs note episodic joint stiffness and mild pain after prolonged ambulation or gardening, managed effectively with PRN Paracetamol (650mg). No acute joint swelling, erythema, or locked joint episodes documented.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-DR-001",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-06-12",
                                "original_statement": "Diagnosed bilateral Knee Osteoarthritis. Physical examination reveals independent mobility and steady gait without assistive devices. Plan: Continue PRN Paracetamol for pain."
                            },
                            {
                                "evidence_id": "EV-DR-002",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-07-08",
                                "original_statement": "Bilateral knee joint discomfort is intermittent and managed with PRN paracetamol. Ambulation remains fully independent."
                            }
                        ],
                        "contradicting_evidence": [
                            "No evidence of acute inflammatory arthritis or joint effusion on clinical examination."
                        ],
                        "missing_information": [
                            "Recent weight-bearing bilateral knee radiographs to assess interval joint space narrowing",
                            "Current quad muscle strength score"
                        ],
                        "evidence_strength": "STRONG",
                        "reasoning": "Synthesized directly from clinician assessment records (EV-DR-001, EV-DR-002) and longitudinal caregiver pain monitoring ([[Caregiver/Pain]]).",
                        "uncertainty": "Knee OA pain is intermittent and stable with conservative management.",
                        "references": ["EV-DR-001", "EV-DR-002"]
                    }
                ],
                "missing_information": [
                    "Updated knee X-ray imaging",
                    "Physical therapy home exercise adherence score"
                ],
                "red_flags": [
                    "Inability to bear weight, hot swollen joint, or fever requires immediate joint aspiration / emergency orthopedic review."
                ],
                "relevant_changes": [
                    "Joint discomfort remains stable on PRN analgesics without daily requirement."
                ],
                "limitations": [
                    "Pain intensity tracking relies on episodic verbal pain scores reported by patient."
                ]
            }

        # Scenario: Nutrition & Dietary Intake
        if any(w in q for w in ["eat", "nutrition", "appetite", "food", "meal", "dinner", "lunch", "diet"]):
            return {
                "considerations": [
                    {
                        "title": "Dietary Intake Patterns & Glycemic Nutrition Management",
                        "category": "Nutrition & Metabolism",
                        "description": "Patient maintains a low-sodium, South Indian vegetarian dietary pattern consistent with diabetic and hypertensive nutritional guidelines. Caregiver notes reflect generally good appetite with isolated instances of eating half portions during warm afternoons.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-DR-002",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-07-08",
                                "original_statement": "Diabetes monitoring continued with recent HbA1c 7.1%. Continue Metformin 500mg BID with meals."
                            },
                            {
                                "evidence_id": "EV-DR-005",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Glycemic control stable (HbA1c 7.4%). Plan: Continue current medication regimen without alteration."
                            }
                        ],
                        "contradicting_evidence": [
                            "No documented significant unintended weight loss or nutritional deficiency markers."
                        ],
                        "missing_information": [
                            "Current serum albumin and pre-albumin levels",
                            "Daily 24-hour hydration log"
                        ],
                        "evidence_strength": "MODERATE",
                        "reasoning": "Derived from longitudinal diabetic monitoring records (EV-DR-002, EV-DR-005) and caregiver dietary logs ([[Caregiver/Nutrition]]).",
                        "uncertainty": "Appetite variations are episodic and transient.",
                        "references": ["EV-DR-002", "EV-DR-005"]
                    }
                ],
                "missing_information": [
                    "Serial monthly weight measurements",
                    "Dietary fiber and protein intake breakdown"
                ],
                "red_flags": [
                    "Progressive dysphagia, persistent anorexia, or >5% weight loss over 3 months warrants urgent gastrointestinal review."
                ],
                "relevant_changes": [
                    "Glycemic control maintained within target (HbA1c 7.1-7.4%) on diabetic dietary baseline."
                ],
                "limitations": [
                    "Home meal tracking is based on caregiver visual portion estimates."
                ]
            }

        # Scenario: Medications & Adherence
        if any(w in q for w in ["medication", "pill", "drug", "adherence", "dose", "tablet", "metformin", "amlodipine", "atorvastatin", "paracetamol"]):
            return {
                "considerations": [
                    {
                        "title": "Active Pharmacotherapy Regimen & Caregiver-Assisted Adherence",
                        "category": "Medications & Adherence",
                        "description": "Patient is maintained on 4 active medications: Metformin 500mg BID (Type 2 Diabetes), Amlodipine 5mg OD (Hypertension), Atorvastatin 20mg ON (Hyperlipidemia), and Paracetamol 650mg PRN (Knee Osteoarthritis). Caregiver organizes a weekly pillbox ensuring >95% adherence without missed doses.",
                        "status": "POSSIBLE_CONSIDERATION",
                        "supporting_evidence": [
                            {
                                "evidence_id": "EV-DR-001",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-06-12",
                                "original_statement": "Diagnosed Type 2 Diabetes, Hypertension, Hyperlipidemia, bilateral knee OA. Plan: Continue current pharmacological therapy."
                            },
                            {
                                "evidence_id": "EV-DR-005",
                                "source_type": "CLINICIAN-CONFIRMED",
                                "observed_at": "2026-09-02",
                                "original_statement": "Family notes they assist with weekly pillbox organization. Glycemic control stable (HbA1c 7.4%). Plan: Continue current medication regimen without alteration."
                            }
                        ],
                        "contradicting_evidence": [
                            "No adverse drug reactions or medication non-compliance events identified in clinical notes."
                        ],
                        "missing_information": [
                            "Annual renal function panel (eGFR/Creatinine) to confirm Metformin safety clearance"
                        ],
                        "evidence_strength": "STRONG",
                        "reasoning": "Grounded in clinician prescription records (EV-DR-001, EV-DR-005) and caregiver adherence logs ([[Clinical/Medications]], [[Caregiver/Medication Adherence]]).",
                        "uncertainty": "Adherence is strong under caregiver pillbox supervision; morning Amlodipine timing is correlated with blood pressure stability.",
                        "references": ["EV-DR-001", "EV-DR-005"]
                    }
                ],
                "missing_information": [
                    "Serum creatinine & eGFR panel within past 6 months",
                    "Liver function tests for long-term statin monitoring"
                ],
                "red_flags": [
                    "Signs of hypoglycemia, severe muscle pain/myopathy, or profound hypotension warrant immediate medication review."
                ],
                "relevant_changes": [
                    "Pharmacotherapy regimen remains stable with caregiver pillbox support."
                ],
                "limitations": [
                    "PRN analgesic usage frequency is logged intermittently by family."
                ]
            }

        # Scenario 1 & 2: Dizziness / Multifactorial / General clinical question
        return {
            "considerations": [
                {
                    "title": "Postural / Orthostatic Instability Process",
                    "category": "Hemodynamic / Postural",
                    "description": "Episodic lightheadedness/dizziness reported after standing up from bed, possibly exacerbated by antihypertensive pharmacotherapy (Amlodipine 5mg).",
                    "status": "POSSIBLE_CONSIDERATION",
                    "supporting_evidence": [
                        {
                            "evidence_id": "EV-CG-041",
                            "source_type": "CAREGIVER-REPORTED",
                            "observed_at": "2026-09-03",
                            "original_statement": "Patient felt dizzy after getting out of bed; resolved after sitting back down for a few minutes."
                        }
                    ],
                    "contradicting_evidence": [
                        "No orthostatic blood pressure or pulse measurements documented in record.",
                        "Dizziness etiology is explicitly UNKNOWN in clinical database."
                    ],
                    "missing_information": [
                        "Orthostatic vital signs (lying, sitting, standing blood pressure and heart rate)",
                        "Medication timing relative to morning dizzy episodes",
                        "Hydration status and daily fluid intake"
                    ],
                    "evidence_strength": "LIMITED",
                    "reasoning": "Symptom onset upon getting out of bed and rapid relief after sitting suggests a postural component, but available evidence is limited to caregiver reports without confirmed vital sign correlation.",
                    "uncertainty": "Etiology is unconfirmed. The record does not establish whether dizziness is vascular, vestibular, or drug-induced.",
                    "references": ["EV-CG-041"]
                },
                {
                    "title": "Transient Balance Impairment with Near-Fall Vulnerability",
                    "category": "Mobility & Fall Risk",
                    "description": "Documented stumbling episode near the bathroom on 2026-09-01 without fall or injury, followed by subsequent recovery.",
                    "status": "POSSIBLE_CONSIDERATION",
                    "supporting_evidence": [
                        {
                            "evidence_id": "EV-CG-045",
                            "source_type": "CAREGIVER-REPORTED",
                            "observed_at": "2026-09-01",
                            "original_statement": "Stumbled near bathroom door; caught by caregiver before hitting floor. No ground impact, no injury."
                        }
                    ],
                    "contradicting_evidence": [
                        "Follow-up observation EV-CG-046 indicates normal indoor walking without furniture cruising the next day."
                    ],
                    "missing_information": [
                        "Illumination and physical obstacles near bathroom at time of near-fall",
                        "Footwear and assistive device usage at home"
                    ],
                    "evidence_strength": "MODERATE",
                    "reasoning": "The near-fall event highlights vulnerability during indoor transitions, though subsequent unassisted walking indicates functional reserve.",
                    "uncertainty": "Near-fall event was witnessed and caught; no ground impact or physical trauma occurred.",
                    "references": ["EV-CG-045", "EV-CG-046"]
                }
            ],
            "missing_information": [
                "Lying and standing orthostatic vital signs (BP and HR)",
                "Precise duration and frequency of dizzy episodes",
                "Timing of Amlodipine administration relative to morning dizziness",
                "Formal vestibulo-ocular or neurological evaluation"
            ],
            "red_flags": [
                "Prompt clinical assessment is warranted if dizziness is accompanied by true syncope, chest discomfort, acute dyspnea, or focal neurological deficits."
            ],
            "relevant_changes": [
                "Recent episodic dizziness upon rising from bed (EV-CG-041)",
                "Near-fall near bathroom on 2026-09-01 without ground impact (EV-CG-045)",
                "Subsequent recovery to independent indoor ambulation on 2026-09-02 (EV-CG-046)"
            ],
            "limitations": [
                "Caregiver observations provide qualitative context but lack continuous objective physiological telemetry."
            ]
        }
