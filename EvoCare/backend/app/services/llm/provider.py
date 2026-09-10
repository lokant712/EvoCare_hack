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
