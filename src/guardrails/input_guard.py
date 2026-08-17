import re
from typing import Dict, Any
from src.llm.schemas import GuardrailResult

# Regex patterns for fast prompt injection and toxicity blocklist (<5ms execution)
INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"system prompt",
    r"bypass safety",
    r"you are now DAN",
    r"jailbreak",
    r"drop database",
    r"delete all files"
]

class InputGuardrail:
    """
    Sub-5ms input guardrail to inspect user queries/transcriptions before retrieval.
    """
    def __init__(self, min_words: int = 2):
        self.min_words = min_words
        self.injection_regex = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

    def validate(self, query_text: str) -> GuardrailResult:
        cleaned = query_text.strip()
        if not cleaned:
            return GuardrailResult(
                is_safe=False,
                reason="खाली ऑडियो/इनपुट प्राप्त हुआ। (Empty or quiet audio input)",
                details={"rule": "empty_input"}
            )

        words = cleaned.split()
        if len(words) < self.min_words:
            return GuardrailResult(
                is_safe=False,
                reason=f"कृपया अधिक स्पष्ट प्रश्न पूछें (कम से कम {self.min_words} शब्द)। Query too short.",
                details={"rule": "min_word_length", "word_count": len(words)}
            )

        # Check injection attack
        if self.injection_regex.search(cleaned):
            return GuardrailResult(
                is_safe=False,
                reason="सुरक्षा नीति के तहत यह अनुरोध अस्वीकृत कर दिया गया है। (Request refused by safety guardrails)",
                details={"rule": "prompt_injection_detected"}
            )

        return GuardrailResult(
            is_safe=True,
            reason="Input passed guardrails",
            details={"word_count": len(words)}
        )
