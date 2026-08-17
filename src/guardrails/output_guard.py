import re
import logging
from typing import List, Tuple
from src.llm.schemas import SourceCitation, GuardrailResult
from src.llm.prompts import GROUNDING_VERIFIER_PROMPT

logger = logging.getLogger("ultron.output_guard")

class OutputGuardrail:
    """
    Two-Tier Grounding & Safety Guardrail:
    - Tier 1 (Deterministic, <5ms): Checks keyword/entity overlap between answer and retrieved passages.
    - Tier 2 (LLM Verifier): Triggered if Tier 1 detects ambiguous entity match or factual discrepancy.
    """
    def __init__(self, min_keyword_overlap_ratio: float = 0.20):
        self.min_keyword_overlap_ratio = min_keyword_overlap_ratio

    def _extract_keywords(self, text: str) -> set:
        # Simple word tokenization excluding common stop words
        words = re.findall(r"\w+", text.lower())
        stopwords = {
            "is", "the", "and", "a", "an", "in", "on", "of", "to", "for", "with",
            "है", "की", "का", "के", "में", "और", "से", "पर", "को", "एक"
        }
        return {w for w in words if w not in stopwords and len(w) > 2}

    def verify_tier1_deterministic(
        self, answer: str, citations: List[SourceCitation]
    ) -> Tuple[bool, str]:
        """
        Tier 1 Sub-5ms Grounding check:
        Calculates entity/keyword overlap ratio between answer and context passages.
        """
        if not citations:
            return False, "No context citations provided for grounding verification."

        answer_keywords = self._extract_keywords(answer)
        if not answer_keywords:
            return True, "Short answer without key entities."

        context_text = " ".join([c.text for c in citations])
        context_keywords = self._extract_keywords(context_text)

        overlap = answer_keywords.intersection(context_keywords)
        overlap_ratio = len(overlap) / len(answer_keywords)

        if overlap_ratio < self.min_keyword_overlap_ratio:
            return False, f"Low keyword overlap ({overlap_ratio:.2f} < {self.min_keyword_overlap_ratio:.2f}) with context."

        return True, f"Deterministic grounding verified (Overlap: {overlap_ratio:.2f})."

    async def verify_grounding(
        self, answer: str, citations: List[SourceCitation], cascade_provider=None
    ) -> GuardrailResult:
        """
        Runs Tier 1 first. If Tier 1 passes, returns safe.
        If Tier 1 fails and cascade_provider is available, runs Tier 2 LLM verifier.
        """
        t1_passed, t1_reason = self.verify_tier1_deterministic(answer, citations)

        if t1_passed:
            return GuardrailResult(
                is_safe=True,
                reason=t1_reason,
                details={"tier": 1}
            )

        logger.warning(f"Tier 1 grounding check failed: {t1_reason}. Triggering Tier 2 LLM verifier...")

        # If cascade_provider is provided, perform Tier 2 LLM verification
        if cascade_provider:
            try:
                context_str = "\n".join([f"[{c.id}] {c.text}" for c in citations])
                verifier_prompt = GROUNDING_VERIFIER_PROMPT.format(
                    context_passages=context_str, candidate_answer=answer
                )
                verifier_response, _, _ = await cascade_provider.generate_answer(
                    query_text=verifier_prompt, context_passages=[]
                )
                if "YES" in verifier_response.upper():
                    return GuardrailResult(
                        is_safe=True,
                        reason="Tier 2 LLM Verifier confirmed grounding.",
                        details={"tier": 2, "t1_reason": t1_reason}
                    )
            except Exception as e:
                logger.error(f"Tier 2 LLM verifier call failed: {e}")

        # Grounding failed
        return GuardrailResult(
            is_safe=False,
            reason="दी गई जानकारी में उत्तर की पूर्ण पुष्टि नहीं हो सकी। (Answer could not be fully grounded in provided context)",
            details={"tier": 1, "t1_reason": t1_reason}
        )
