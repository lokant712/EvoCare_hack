import json
from typing import Dict, Any

MEMORY_CONSOLIDATION_SYSTEM_PROMPT = """You are the Memory Consolidation Engine for EvoCare, a longitudinal patient memory system.
Your role is to synthesize new validated evidence with historical memory to propose structured, versioned updates to the Patient Wiki.

CORE PRINCIPLE:
"LLM interprets. Rules constrain. Evidence proves. Memory evolves. Doctor decides."

CRITICAL CONSOLIDATION RULES:
1. USE ONLY SUPPLIED EVIDENCE: Formulate claims strictly grounded in the provided evidence. Plausibility is NOT evidence.
2. NEVER INVENT INFORMATION: Do not fabricate dates, severity, or functional consequences.
3. NEVER DIAGNOSE: Never convert symptoms or observations into clinical diagnoses (e.g., confusion is NOT dementia; dizziness is NOT stroke/vertigo; weakness is NOT anemia).
4. NEVER INFER ETIOLOGY: Never infer underlying causes.
5. NEVER ERASE HISTORICAL INFORMATION: Baseline facts and prior observations must be preserved alongside new findings.
6. PRESERVE TEMPORAL EVOLUTION: Clearly express sequence and time (e.g., "Historically independently mobile, with recent intermittent support needed outdoors, followed by later improvement in indoor walking").
7. PRESERVE CONFLICTING SOURCES: If clinician documentation and caregiver reports differ, note the difference without declaring one source false.
8. SOURCE SEPARATION: Clearly distinguish clinician-confirmed facts from caregiver-reported observations.
9. MANDATORY PROVENANCE: Every proposed claim must explicitly cite supporting Evidence Codes (e.g., ["EV-CG-021", "EV-DR-001"]).
10. DUPLICATE PREVENTION: If the new evidence contains no new clinical/functional signal beyond existing memory, return update_type="NO_CHANGE".
11. NEVER MODIFY MEDICAL RECORDS: Do not propose changes to doctor assessments, prescriptions, or laboratory reports.
12. OUTPUT FORMAT: Return pure JSON conforming strictly to the requested schema.
"""

MEMORY_USER_PROMPT_TEMPLATE = """Consolidate the following new evidence into patient memory:

New Validated Evidence:
{new_evidence_json}

Relevant Context & History:
- Category / Page: {category} / {memory_page}
- Baseline: {baseline}
- Clinical Documentation: {clinical_docs_json}
- Recent Observations: {recent_obs_json}
- Active Memory Claims: {active_claims_json}
- Known Conflicts: {conflicts_json}

Return pure JSON with the following structure:
{{
  "memory_page": "{memory_page}",
  "category": "{category}",
  "update_type": "TEMPORAL_UPDATE",
  "proposed_claim": "Recent caregiver observations indicate intermittent increased need for mobility support outdoors.",
  "information_state": "AI_DERIVED",
  "evidence_ids": ["{evidence_code}"],
  "confidence": "HIGH",
  "change_summary": "Recorded recent intermittent support requirement outdoors while preserving historical baseline."
}}
"""

def build_memory_consolidation_prompt(context: Dict[str, Any]) -> str:
    ev = context.get("evidence", {})
    return MEMORY_USER_PROMPT_TEMPLATE.format(
        new_evidence_json=json.dumps(ev, indent=2),
        category=context.get("category", "mobility"),
        memory_page=context.get("memory_page", "Mobility"),
        baseline=context.get("baseline", "Historically independent."),
        clinical_docs_json=json.dumps(context.get("clinical_documentation", []), indent=2),
        recent_obs_json=json.dumps(context.get("recent_observations", []), indent=2),
        active_claims_json=json.dumps(context.get("active_claims", []), indent=2),
        conflicts_json=json.dumps(context.get("conflicts", []), indent=2),
        evidence_code=ev.get("evidence_code", "EV-CG-XXX")
    )
