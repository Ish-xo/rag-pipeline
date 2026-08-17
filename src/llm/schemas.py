from pydantic import BaseModel, Field
from typing import List, Optional

class SourceCitation(BaseModel):
    id: int = Field(..., description="ID of the cited source passage")
    text: str = Field(..., description="Excerpt or full text of the cited passage")
    similarity: float = Field(..., description="Similarity score of the retrieved source")
    query_id: Optional[str] = Field(None, description="Original query ID if from MSMARCO")

class RAGQuery(BaseModel):
    query_text: str = Field(..., description="User question or transcribed text")
    fast_path: bool = Field(True, description="True for fast path retrieval, False for quality path ensemble")
    language: str = Field("hi", description="Query language code ('hi', 'en', or 'hinglish')")

class GuardrailResult(BaseModel):
    is_safe: bool = Field(True, description="Whether the input/output passed guardrails")
    reason: str = Field("", description="Reason if refused or flagged")
    details: Optional[dict] = Field(default_factory=dict, description="Metadata details")

class RAGResponse(BaseModel):
    answer: str = Field(..., description="Generated answer text")
    citations: List[SourceCitation] = Field(default_factory=list, description="List of source citations used")
    provider_used: str = Field("mock", description="Name of the LLM provider that generated the response")
    execution_time_ms: float = Field(0.0, description="Total generation time in milliseconds")
    grounded: bool = Field(True, description="True if answer passed grounding check")
    guardrail_result: Optional[GuardrailResult] = Field(None, description="Guardrail inspection result")
