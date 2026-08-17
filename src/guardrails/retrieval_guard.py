from typing import List, Tuple
from src.llm.schemas import SourceCitation, GuardrailResult

class RetrievalGuardrail:
    """
    Sub-5ms retrieval guardrail to filter low-similarity or duplicate passages.
    """
    def __init__(self, min_similarity_threshold: float = 0.40):
        self.min_similarity_threshold = min_similarity_threshold

    def filter_and_validate(
        self, citations: List[SourceCitation]
    ) -> Tuple[List[SourceCitation], GuardrailResult]:
        if not citations:
            return [], GuardrailResult(
                is_safe=False,
                reason="दी गई जानकारी में संबंधित दस्तावेज़ नहीं मिले। (No relevant passages found in database)",
                details={"rule": "zero_citations"}
            )

        # Filter out passages below similarity threshold
        filtered = [
            c for c in citations if c.similarity >= self.min_similarity_threshold
        ]

        if not filtered:
            top_score = max([c.similarity for c in citations]) if citations else 0.0
            return [], GuardrailResult(
                is_safe=False,
                reason=f"प्रासंगिक जानकारी का स्कोर बहुत कम है ({top_score:.2f} < threshold {self.min_similarity_threshold:.2f})। Out of domain query.",
                details={"rule": "low_similarity_score", "top_score": top_score}
            )

        # Deduplicate identical context texts
        seen_texts = set()
        unique_citations = []
        for c in filtered:
            normalized = c.text.strip().lower()
            if normalized not in seen_texts:
                seen_texts.add(normalized)
                unique_citations.append(c)

        return unique_citations, GuardrailResult(
            is_safe=True,
            reason="Retrieval passages passed guardrails",
            details={
                "initial_count": len(citations),
                "retained_count": len(unique_citations)
            }
        )
