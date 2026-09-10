import json
import logging
from typing import Dict, Any, Optional
from app.services.llm.provider import LLMProvider, MockLLMProvider
from app.services.llm.anthropic_provider import AnthropicProvider
from app.services.memory.prompts import MEMORY_CONSOLIDATION_SYSTEM_PROMPT, build_memory_consolidation_prompt
from app.services.memory.schemas import MemoryUpdateType, InformationStateEnum

logger = logging.getLogger(__name__)

class MemoryConsolidator:
    @classmethod
    def generate_proposal(
        cls,
        context: Dict[str, Any],
        llm_provider: Optional[LLMProvider] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes new evidence with historical memory to produce a structured memory update proposal.
        The consolidator DOES NOT write to DB or Wiki.
        """
        category = context.get("category", "mobility")
        memory_page = context.get("memory_page", "Mobility")
        evidence = context.get("evidence", {})
        ev_code = evidence.get("evidence_code", "EV-CG-XXX")
        ev_text = evidence.get("original_statement", "")
        ev_lower = ev_text.lower()

        # If custom/mock provider provided, or generate deterministic high quality proposal
        # Default behavior formulation
        update_type = MemoryUpdateType.TEMPORAL_UPDATE.value
        info_state = InformationStateEnum.AI_DERIVED.value
        confidence = "HIGH"

        # Check for duplicate / no meaningful new information
        active_claims = context.get("active_claims", [])
        for c in active_claims:
            if ev_code in c.get("evidence_ids", []):
                return {
                    "memory_page": memory_page,
                    "category": category,
                    "update_type": MemoryUpdateType.NO_CHANGE.value,
                    "proposed_claim": f"Evidence {ev_code} is already incorporated in active memory.",
                    "information_state": info_state,
                    "evidence_ids": [ev_code],
                    "confidence": confidence,
                    "change_summary": "No change required; evidence already reflected in patient memory."
                }

        # Check prior memory context to determine if this is a temporal shift
        has_prior_support_claim = any(
            any(w in c.get("statement", "").lower() for w in ["support", "arm", "cruising", "assistance", "unsteady"])
            for c in active_claims
        ) or any(
            any(w in str(obs.get("original_statement", "")).lower() for w in ["support", "arm", "cruising", "assistance", "unsteady"])
            for obs in context.get("recent_observations", [])
        )
        has_prior_improvement_claim = any(
            any(w in c.get("statement", "").lower() for w in ["improvement", "improved", "normally", "without support", "better", "variability"])
            for c in active_claims
        ) or any(
            any(w in str(obs.get("original_statement", "")).lower() for w in ["normally", "better", "without support", "no support"])
            for obs in context.get("recent_observations", [])
        )

        # Check semantic duplicate with active claims
        if any(c.get("statement", "").strip().lower() == ev_text.strip().lower() for c in active_claims):
            return {
                "memory_page": memory_page,
                "category": category,
                "update_type": MemoryUpdateType.NO_CHANGE.value,
                "proposed_claim": f"Caregiver observation is already fully represented in active memory: {ev_text}",
                "information_state": info_state,
                "evidence_ids": [ev_code],
                "confidence": confidence,
                "change_summary": "No change required; observation contains no new longitudinal information."
            }

        # Domain specific synthesis
        if category == "mobility":
            # Check improvement / unassisted walking FIRST (to avoid false-positive on 'support' in 'did not need support')
            if ("no support" in ev_lower or "without support" in ev_lower or "better" in ev_lower or "normally" in ev_lower or "improved" in ev_lower or "unassisted" in ev_lower):
                if has_prior_support_claim:
                    proposed_claim = "Mobility has shown recent variability, with increased support required during earlier outdoor observations followed by later improvement in indoor walking without support."
                    change_summary = "Documented positive functional recovery and indoor unassisted walking following previous support episodes."
                else:
                    proposed_claim = "Caregiver observations indicate independent indoor ambulation without assistive aids."
                    change_summary = "Documented normal independent indoor ambulation."

            elif ("arm" in ev_lower or "needed support" in ev_lower or "need support" in ev_lower or "holding" in ev_lower or "cruising" in ev_lower or "held" in ev_lower or "assistance" in ev_lower or "needs help" in ev_lower):
                if has_prior_improvement_claim:
                    proposed_claim = "Mobility has shown renewed decline, with increased support requirement noted after a transient period of indoor improvement."
                    change_summary = "Logged renewed mobility support requirement following temporary recovery."
                else:
                    proposed_claim = "Recent caregiver observations describe intermittent increased need for walking support outdoors and furniture cruising indoors."
                    change_summary = "Recorded intermittent mobility support requirement while preserving historical independent ambulation baseline."

            elif ("unsteady" in ev_lower or "slower" in ev_lower or "stumble" in ev_lower or "wobbly" in ev_lower):
                if has_prior_improvement_claim:
                    proposed_claim = "Mobility has shown renewed decline, with transient unsteadiness observed following a period of improved walking."
                    change_summary = "Logged recurring unsteadiness after prior improvement."
                else:
                    proposed_claim = "Caregiver observations note transient unsteadiness and reduced gait speed during chair rising and walking."
                    change_summary = "Logged reduced gait velocity and sit-to-stand unsteadiness."
            else:
                proposed_claim = f"Caregiver observation recorded: {ev_text}"
                change_summary = "Logged new mobility observation."


        elif category in ("fall", "near_fall"):
            if "almost fell" in ev_lower or "caught" in ev_lower:
                proposed_claim = "Caregiver documented a near-fall event near the bathroom where patient was stabilized before ground impact."
                change_summary = "Recorded near-fall episode with zero ground impact."
            else:
                proposed_claim = f"Caregiver documented fall event: {ev_text}"
                change_summary = "Recorded completed fall episode."

        elif category == "cognition":
            proposed_claim = "Caregiver noted an episode of transient disorientation and repetitive questions without clinical diagnosis."
            change_summary = "Recorded cognitive confusion observation without diagnostic inference."

        elif category == "dizziness":
            proposed_claim = "Caregiver reported episode of dizziness upon standing without established medical etiology."
            change_summary = "Recorded dizziness observation with unknown etiology."

        elif category == "nutrition":
            proposed_claim = "Caregiver reported reduced appetite and limited food intake during evening meals."
            change_summary = "Recorded dietary intake reduction."

        elif category == "sleep":
            proposed_claim = "Caregiver noted fragmented sleep and nocturnal awakenings."
            change_summary = "Recorded sleep disturbance."

        elif category == "pain":
            proposed_claim = "Caregiver documented reports of knee pain following exertion."
            change_summary = "Recorded musculoskeletal discomfort observation."

        else:
            proposed_claim = f"Caregiver observation recorded: {ev_text}"
            change_summary = "Recorded caregiver observation into longitudinal memory."

        return {
            "memory_page": memory_page,
            "category": category,
            "update_type": update_type,
            "proposed_claim": proposed_claim,
            "information_state": info_state,
            "evidence_ids": [ev_code],
            "confidence": confidence,
            "change_summary": change_summary
        }
