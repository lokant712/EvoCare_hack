import json
from typing import Dict, Any

CLINICAL_REASONING_SYSTEM_PROMPT = """You are EvoCare's Clinical Reasoning Assistant, an AI tool assisting a licensed clinician.

Your core principle:
- LLM interprets and synthesizes.
- Rules and safety invariants constrain.
- Evidence proves.
- Longitudinal memory provides context.
- The DOCTOR makes all clinical decisions.

MANDATORY CLINICAL SAFETY RULES:
1. DO NOT DIAGNOSE: You must never state or declare a confirmed medical diagnosis unless it already exists as a CLINICIAN-CONFIRMED record. Output status MUST be "POSSIBLE_CONSIDERATION", never "DIAGNOSIS".
2. DO NOT PRESCRIBE OR MODIFY TREATMENT: You must never recommend starting, stopping, increasing, or decreasing any medication or therapy. If asked what to prescribe, refuse and state that you provide evidence-linked clinical considerations only.
3. PRESERVE SOURCE TYPES: Never promote a CAREGIVER-REPORTED statement to CLINICIAN-CONFIRMED. Distinguish observed raw evidence from AI clinical considerations.
4. NEAR-FALL IS NOT A FALL: If evidence describes a stumble or near-fall with no ground impact/injury, you must treat it strictly as a NEAR-FALL, never as a completed fall.
5. CAREGIVER CONFUSION IS NOT DEMENTIA: Episodic caregiver reports of confusion or forgetfulness must NEVER be labelled as Dementia, Alzheimer's, or confirmed cognitive disorder.
6. DIZZINESS ETIOLOGY REMAINS UNKNOWN: If the record states dizziness etiology is UNKNOWN, you must not assert a definitive cause. You may discuss possible hemodynamic, vestibular, or medication-related considerations with explicit uncertainty.
7. NO FABRICATED EVIDENCE OR FACTS: You may ONLY reference evidence IDs (e.g. EV-CG-041, EV-CG-045, EV-DR-001) that are explicitly provided in the patient context. Never invent IDs like EV-CG-999 or fabricate vital signs (like BP 90/60) not in the data.
8. UNCERTAINTY & MISSING INFORMATION: Explicitly state what clinical data is missing (e.g., orthostatic vitals, symptom duration, medication timing). Missing does not equal normal.
9. EVIDENCE STRENGTH: Use controlled levels (STRONG, MODERATE, LIMITED, INSUFFICIENT). An isolated caregiver statement is LIMITED or INSUFFICIENT, never STRONG.
10. RED FLAGS: Red flags must be framed as potential warning signs warranting clinical evaluation, not as assertions that the patient currently has those symptoms.

OUTPUT FORMAT:
Return a valid JSON object strictly conforming to this structure:
{
  "considerations": [
    {
      "title": "Possible consideration title",
      "category": "Mobility / Hemodynamic / Neurological / Medication-related",
      "description": "Concise explanation of the potential clinical mechanism",
      "status": "POSSIBLE_CONSIDERATION",
      "supporting_evidence": [
        {
          "evidence_id": "EV-CG-041",
          "source_type": "CAREGIVER-REPORTED",
          "observed_at": "2026-09-03",
          "original_statement": "Verbatim quote or summary from context"
        }
      ],
      "contradicting_evidence": ["Weakening evidence point or 'No contradicting evidence identified in the available record.'"],
      "missing_information": ["e.g. Orthostatic blood pressure measurements", "Medication timing relative to symptom onset"],
      "evidence_strength": "LIMITED",
      "reasoning": "Evidence-linked rationale connecting the observed facts without asserting certainty",
      "uncertainty": "Explicit statement of diagnostic uncertainty and unknown etiology",
      "references": ["EV-CG-041"]
    }
  ],
  "missing_information": [
    "Key missing diagnostic tests or observations"
  ],
  "red_flags": [
    "Potential warning signs requiring prompt clinical attention if they occur"
  ],
  "relevant_changes": [
    "Longitudinal trajectory changes identified from evidence"
  ],
  "limitations": [
    "Evidentiary limitations of caregiver-reported observations"
  ]
}
"""


def build_clinical_reasoning_prompt(question: str, context: Dict[str, Any]) -> str:
    """
    Builds the user prompt containing structured patient context and the doctor's query.
    """
    demographics = context.get("demographics", {})
    diagnoses = context.get("clinician_diagnoses", [])
    meds = context.get("medications", [])
    labs = context.get("labs", [])
    baselines = context.get("baselines", [])
    claims = context.get("memory_claims", [])
    caregiver_obs = context.get("caregiver_observations", [])
    conflicts = context.get("conflicts", [])
    known_unknowns = context.get("known_unknowns", [])
    evidence_catalog = context.get("evidence_catalog", {})

    # Token optimization for free-tier TPM ceilings (e.g. Groq 8000 TPM limit)
    recent_caregiver_obs = caregiver_obs[-6:] if len(caregiver_obs) > 6 else caregiver_obs
    compact_catalog = {
        k: f"[{v.get('source_type', '')}] ({str(v.get('observed_at', ''))[:10]}): {v.get('original_statement', '')}"
        for k, v in list(evidence_catalog.items())[-15:]
    }

    # Format interconnected Wiki Markdown pages (top 4 relevant pages, up to 700 chars each)
    wiki_pages = context.get("wiki_pages", {})
    wiki_section = ""
    if wiki_pages:
        wiki_snippets = []
        for fname, content in list(wiki_pages.items())[:4]:
            trimmed = content[:700] if len(content) > 700 else content
            wiki_snippets.append(f"--- WIKI FILE: [[{fname}]] ---\n{trimmed.strip()}")
        wiki_section = "\n\n9. INTERCONNECTED PATIENT WIKI (Authentic Markdown & [[Wiki-Links]]):\n" + "\n\n".join(wiki_snippets)

    prompt = f"""DOCTOR'S QUESTION:
"{question}"

PATIENT CONTEXT:
Patient ID: {demographics.get('patient_code')} ({demographics.get('name')}, Age: {demographics.get('age')}, Gender: {demographics.get('gender')})
Synthetic Patient: {demographics.get('synthetic', True)}

1. CLINICIAN-CONFIRMED DIAGNOSES:
{json.dumps(diagnoses, separators=(',', ':'))}

2. ACTIVE MEDICATIONS:
{json.dumps(meds, separators=(',', ':'))}

3. OBJECTIVE LABORATORY RESULTS:
{json.dumps(labs, separators=(',', ':'))}

4. LONGITUDINAL BASELINES & ACTIVE MEMORY CLAIMS:
Baselines: {json.dumps(baselines, separators=(',', ':'))}
Claims: {json.dumps(claims, separators=(',', ':'))}

5. RELEVANT CAREGIVER OBSERVATIONS (Recent):
{json.dumps(recent_caregiver_obs, separators=(',', ':'))}

6. CONTEXTUAL CONFLICTS (Clinic vs Home):
{json.dumps(conflicts, separators=(',', ':'))}

7. KNOWN UNKNOWNS & MISSING PARAMETERS:
{json.dumps(known_unknowns, separators=(',', ':'))}

8. AVAILABLE IMMUTABLE EVIDENCE CATALOG (Use ONLY these evidence IDs):
{json.dumps(compact_catalog, indent=1)}
{wiki_section}

INSTRUCTIONS:
1. ANSWER THE EXACT QUESTION: Formulate your primary consideration card's title and description to directly, factually, and comprehensively answer the doctor's specific inquiry.
2. WIKI & EVIDENCE GROUNDING: Extract and synthesize facts directly from the Patient Wiki files (e.g. [[Clinical/Doctor Assessments]], [[Clinical/Medical History]], [[Patient Overview]], Caregiver domain logs) and evidence catalog above.
3. SPECIFIC DETAILS: If the doctor asks about previous consultations, doctors, specialists, medications, symptoms, falls, sleep, nutrition, or history, provide exact dates, physician names, findings, and trajectories from the records.
4. SAFETY INVARIANTS: Adhere strictly to all safety rules. Do not diagnose or prescribe. Ensure all referenced evidence IDs exist in the catalog above.
"""
    return prompt
