import re
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
        elif re.search(r"\b(eat|ate|eating|lunch|dinner|breakfast|food|appetite|bites|meal|intake|hungry)\b", t) or "didn't eat" in t or "did not eat" in t:
            return "nutrition"
        elif re.search(r"\b(confused|confusion|forgot|forget|remember|memory|disoriented|repeating)\b", t):
            return "cognition"
        elif re.search(r"\b(hurt|pain|ache|aching|sore|discomfort|knees|knee|joint)\b", t):
            return "pain"
        elif re.search(r"\b(sleep|slept|woke|waking|insomnia|night|bedtime)\b", t):
            return "sleep"
        elif re.search(r"\b(medicine|medicines|pills|dose|tablet|medication|reminded|pillbox)\b", t):
            return "medication_adherence"
        elif re.search(r"\b(mood|frustrated|quiet|laughing|crying|temper|demure|social|agitated|restless|withdrawn|cheerful|behavior)\b", t):
            return "behavior"
        elif re.search(r"\b(walk|walking|unsteady|stumble|limp|support|gait|chair|table)\b", t):
            return "mobility"
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
            if "10 minutes" in t or "10 mins" in t:
                extracted["duration"] = "approximately 10 minutes"
            elif "seconds" in t or "few seconds" in t:
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
