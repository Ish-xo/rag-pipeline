# ULTRON-V — Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         ULTRON-V Pipeline                              │
│                                                                        │
│  🎤 Audio ──► [STT] ──► [Query Processor] ──► [Retriever] ──►         │
│                              │                     │                   │
│                              ▼                     ▼                   │
│                         [Guardrails]          [Vector DB]              │
│                              │                     │                   │
│                              ▼                     ▼                   │
│                         [LLM Harness] ◄─── Retrieved Context          │
│                              │                                         │
│                              ▼                                         │
│                      [Answer + Citations]                              │
│                              │                                         │
│                              ▼                                         │
│                          [TTS] ──► 🔊 Audio                           │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Speech-to-Text (STT)

### Primary: Sarvam AI (`saaras:v3`)
- **Endpoint**: `POST https://api.sarvam.ai/speech-to-text`
- **Free Credits**: ₹100 on signup (~200 minutes of audio)
- **Rate Limit**: 60 RPM
- **Max Audio Length**: 30 seconds per request (REST API)
- **Languages**: Hindi (`hi-IN`), English (`en-IN`), auto-detect
- **Features**: 
  - `mode=transcribe` — verbatim transcription
  - `mode=translate` — Indic speech → English text (useful!)
  - `mode=codemix` — Hinglish support
  - Auto language detection when `language_code` omitted
- **Auth**: `api-subscription-key` header

### Why Sarvam?
- Task explicitly recommends Sarvam or ElevenLabs
- Sarvam has native Indic language support, better for Hindi
- Auto language detection means we don't need user to specify language
- `translate` mode gives us English text from Hindi speech (helps retrieval)

---

## 2. Chunking Strategy

> **Task requirement**: *"Chunking strategy should be vast — don't submit a single naive fixed-size chunking approach."*

The MSMARCO-XI dataset is **pre-chunked into passages** (~10 passages per query). But we need to show sophisticated handling. Our multi-strategy approach:

### Strategy 1: Passage-Level Indexing (Base)
- Each passage is a retrieval unit (~60-80 words avg)
- Natural semantic boundaries from the original MS MARCO dataset
- Metadata: `query_id`, `query_type`, `is_selected`, `language`

### Strategy 2: Sliding Window with Overlap
- For longer passages, apply sliding window (256 tokens, 64 token overlap)
- Ensures no context is lost at chunk boundaries
- Parent-child tracking: each sub-chunk references its parent passage

### Strategy 3: Semantic Chunking
- Group consecutive passages that are semantically related (cosine similarity > threshold)
- Merge related passages into "mega-chunks" for broader context retrieval
- Use embedding similarity between adjacent passages to detect topic shifts

### Strategy 4: Metadata-Enriched Chunks
- Augment each chunk with:
  - `query_type` (DESCRIPTION, NUMERIC, ENTITY, LOCATION, PERSON)
  - `is_selected` flag (ground truth relevance)
  - Original English passage (for cross-lingual retrieval)
  - Translated passage (for native language generation)
  - Source query (for contextual understanding)

### Strategy 5: Hypothetical Document Embedding (HyDE)
- At query time: generate a hypothetical answer using the LLM
- Embed the hypothetical answer instead of the raw query
- Search for passages similar to the hypothetical answer
- Better retrieval quality for complex questions

### Chunk Metadata Schema
```json
{
  "chunk_id": "hi_1185869_p3_s1",
  "text": "The actual chunk text...",
  "passage_index": 3,
  "query_id": 1185869,
  "query_type": "DESCRIPTION",
  "is_selected": 1,
  "language": "hi",
  "english_text": "Original English passage...",
  "translated_text": "Hindi translated passage...",
  "parent_chunk_id": "hi_1185869_p3",
  "chunk_strategy": "sliding_window",
  "token_count": 128
}
```

---

## 3. Embedding

### Primary: Voyage AI `voyage-multilingual-2`
- **Dimensions**: 1024
- **Free Quota**: 50M tokens on signup
- **Context Window**: 4,000 tokens
- **Rate Limit**: 2,000 RPM
- **Strengths**: State-of-the-art on multilingual MTEB benchmarks, excellent for Indic languages
- **Usage**: Batch embed all passages during ingestion

### Backup 1: Google Gemini `text-embedding-004`
- **Dimensions**: 768
- **Free Quota**: Unlimited (free tier)
- **Rate Limit**: 1,500 RPM
- **Strengths**: No monthly token cap, very high RPM
- **Usage**: Fallback if Voyage quota exhausted, also used for query-time embeddings

### Backup 2: Jina AI `jina-embeddings-v3`
- **Dimensions**: 1024 (Matryoshka to 256-768)
- **Free Quota**: 10M tokens on signup
- **Rate Limit**: 100 RPM
- **Strengths**: Task-specific LoRA adapters (`retrieval.query` vs `retrieval.passage`)

### Embedding Strategy
- **Index-time**: Use Voyage AI for all passage embeddings (highest quality)
- **Query-time**: Use Gemini `text-embedding-004` (unlimited, fast) with fallback to Voyage
- **Dimensionality**: 1024d for Voyage, 768d for Gemini (separate collections or unified with padding)

> **Important**: We index **English passages** for embedding (better multilingual embedding quality). Translated text is stored as metadata payload for answer generation.

---

## 4. Vector Database

### Primary: Qdrant Cloud (Free Tier)
- **Storage**: 4 GB disk, 1 GB RAM, 0.5 vCPU
- **Capacity**: ~500K vectors at 1024d (uncompressed), ~1M with scalar quantization
- **Features**: 
  - HNSW index for fast ANN search
  - Payload filtering (filter by `language`, `query_type`, etc.)
  - Scalar quantization (int8) to fit more vectors
  - Multi-vector support
- **Inactivity Policy**: Suspended after 7 days idle, deleted after 4 weeks
  - Mitigation: Set up a keep-alive cron ping

### Backup: Pinecone Serverless (Free Tier)
- **Storage**: 2 GB
- **Capacity**: ~250K-300K vectors at 1024d
- **Rate Limits**: 2M write units/mo, 1M read units/mo
- **Usage**: Activated if Qdrant goes down or approaches limits

### Collection Design
```
Collection: ultron_passages
├── Vectors: 1024d (Voyage) or 768d (Gemini)
├── Distance: Cosine
├── Quantization: Scalar (int8)
└── Payload Fields:
    ├── chunk_id (keyword, indexed)
    ├── text (text)
    ├── english_text (text)
    ├── translated_text (text)
    ├── query_id (integer, indexed)
    ├── query_type (keyword, indexed)
    ├── is_selected (integer)
    ├── language (keyword, indexed)
    ├── chunk_strategy (keyword, indexed)
    └── passage_index (integer)
```

### Data Volume Estimate (English + Hindi)
- ~100K unique passages (deduplicated from MSMARCO queries)
- Each passage embedded at 1024d → ~4 KB per vector
- Metadata per vector → ~1-2 KB
- Total: ~100K × 6 KB ≈ **600 MB** (fits in Qdrant's 4 GB)

---

## 5. LLM — Answer Generation

### The Latency Challenge
The task demands **<200ms** for "chunking + vector DB retrieval + everything through to final output." This is extremely aggressive. Our interpretation:
- **Retrieval (embedding + vector search)**: ~50-100ms (achievable)
- **LLM generation**: Even the fastest APIs (Groq) take 300-1000ms for a complete answer
- **Strategy**: Use **streaming** to deliver first tokens within 200ms. Report P50/P70/P100 for both Time-to-First-Token (TTFT) and total completion time.

### Provider Cascade (5 backups for resilience)

| Priority | Provider | Model | Latency (TTFT) | RPM | RPD | Why |
|----------|----------|-------|-----------------|-----|-----|-----|
| 1 | **Groq** | `llama-3.3-70b-versatile` | ~100-200ms | 30 | 1,000 | Fastest inference (LPU), best for latency target |
| 2 | **Cerebras** | `llama-3.3-70b` | ~100-300ms | 30 | ~1M tokens/day | Ultra-fast, generous daily quota |
| 3 | **SambaNova** | `Meta-Llama-3.3-70B-Instruct` | ~200-500ms | 240 | 48,000 | Highest RPM, very generous limits |
| 4 | **Google Gemini** | `gemini-2.0-flash` | ~200-500ms | 15 | 1,500 | 1M context, structured output, reliable |
| 5 | **Together AI** | `Llama-3.3-70B-Instruct-Turbo-Free` | ~300-700ms | 60 | dynamic | Good fallback with $5 initial credit |
| 6 | **OpenRouter** | `:free` models (auto-route) | ~500ms+ | 20 | 50 | Last-resort fallback |

### Failover Logic
```python
providers = [groq, cerebras, sambanova, gemini, together, openrouter]
for provider in providers:
    try:
        response = await provider.generate(prompt, timeout=5.0)
        return response
    except (RateLimitError, TimeoutError, APIError):
        continue
raise AllProvidersExhaustedError()
```

### LLM Interface (OpenAI-compatible)
All providers except Gemini support OpenAI-compatible API format. Use `litellm` or `openai` SDK with provider-specific base URLs. For Gemini, use `google-genai` SDK or adapt via OpenAI compatibility endpoint.

---

## 6. Model Harness

> **Task requirement**: *"Structured orchestration around the model — tool calls, retries, structured input/output handling, error recovery."*

### Harness Components

#### A. Structured Input/Output (via Pydantic + Instructor)
```python
class RAGQuery(BaseModel):
    """Validated input to the RAG pipeline"""
    query_text: str
    language: str  # detected from STT
    original_audio_duration: float
    
class RAGResponse(BaseModel):
    """Structured output from the LLM"""
    answer: str
    confidence: float  # 0.0 - 1.0
    sources: list[SourceCitation]
    is_grounded: bool
    language: str
    
class SourceCitation(BaseModel):
    passage_text: str
    passage_id: str
    relevance_score: float
```

#### B. Retry Logic
- Exponential backoff with jitter on API failures
- Provider cascade (try next provider on failure)
- Max 3 retries per provider before moving to next
- Circuit breaker pattern: disable provider after N consecutive failures

#### C. Tool Calls
- `retrieve_passages(query, top_k, filters)` — vector search
- `check_relevance(query, passages)` — re-rank/filter passages
- `detect_language(text)` — language identification
- `translate_query(text, source_lang, target_lang)` — for cross-lingual retrieval

#### D. Error Recovery
- Graceful degradation: if all LLMs fail, return top retrieved passages as-is
- Timeout handling: 5s max per LLM call, 10s total pipeline timeout
- Input validation: reject audio >30s, empty transcripts, etc.

---

## 7. Guardrails

> **Task requirement**: *"Handling for off-topic queries, unsafe/inappropriate inputs, hallucination checks, or answers not grounded in the retrieved context."*

### Guardrail Layers

#### Layer 1: Input Guardrails (Pre-Retrieval)
- **Empty/noise detection**: Reject transcripts < 3 words or confidence < 0.3
- **Language detection**: Ensure input is in supported languages
- **Toxicity/safety filter**: Check for unsafe/inappropriate content via keyword matching + LLM classification
- **Query type classification**: Identify if query is factual, opinion, or off-topic

#### Layer 2: Retrieval Guardrails (Post-Retrieval)
- **Relevance threshold**: If best passage score < 0.5 cosine similarity, flag as "low confidence"
- **Passage diversity**: Ensure retrieved passages aren't all from same query_id
- **No-context handling**: If no relevant passages found, return "I don't have information about this topic"

#### Layer 3: Output Guardrails (Post-Generation)
- **Grounding check**: Verify answer claims are supported by retrieved passages
  - Use NLI (Natural Language Inference) or simple overlap scoring
  - Flag ungrounded claims
- **Hallucination detection**: Compare answer entities/facts against passage text
- **Refusal triggers**: 
  - Off-topic (not in knowledge base domain)
  - Unsafe/harmful queries
  - Ungrounded answers (confidence below threshold)
- **Response format validation**: Ensure structured output matches schema

### Guardrail Response Format
```python
class GuardrailResult(BaseModel):
    is_safe: bool
    is_on_topic: bool
    is_grounded: bool
    confidence: float
    refusal_reason: Optional[str]
    warnings: list[str]
```

---

## 8. Text-to-Speech (TTS)

### Primary: `edge-tts` (Microsoft Edge Neural Voices)
- **Cost**: Completely free, no API key required
- **Rate Limit**: Unlimited for development workloads
- **Voices**: 
  - Hindi: `hi-IN-SwaraNeural` (Female), `hi-IN-MadhurNeural` (Male)
  - English: `en-IN-NeerjaNeural` (Female), `en-IN-PrabhatNeural` (Male)
- **Quality**: Azure Neural voices — high naturalness
- **Integration**: Python `edge-tts` package, async API

### Secondary: Sarvam TTS (`bulbul:v3`)
- **Endpoint**: `POST https://api.sarvam.ai/text-to-speech`
- **Free Credits**: Shared ₹100 pool with STT (~33K characters)
- **Best for**: Authentic Indian accent, Hinglish support
- **Max per request**: 2,500 characters

### Tertiary: ElevenLabs (Multilingual v3)
- **Free Tier**: 10,000 characters/month
- **Languages**: Hindi, Bengali, Tamil, Telugu + 70 more
- **Quality**: Best emotional expressiveness
- **Limitation**: Very small free quota, save for demos

### TTS Strategy
- Use `edge-tts` for all general TTS (unlimited, good quality)
- Use Sarvam TTS for showcase/demo (better Indian accent)
- ElevenLabs reserved for polished demo recordings only

---

## 9. Latency Analytics

### Measurement Points
```
T0: Audio received
T1: STT complete (transcript ready)
T2: Query processed (embedding generated)
T3: Vector search complete (passages retrieved)
T4: LLM first token generated
T5: LLM complete (full answer)
T6: TTS complete (audio generated)

Metrics:
- STT Latency: T1 - T0
- Retrieval Latency: T3 - T1  (this is what the task targets at <200ms)
- Generation TTFT: T4 - T3
- Generation Total: T5 - T3
- TTS Latency: T6 - T5
- End-to-End: T6 - T0
```

### Reporting
- Run **100+ test queries** from the MSMARCO-XI validation set
- Report **P50 / P70 / P100** for each metric
- Display analytics dashboard in the Gradio UI
- Log all latency data to a CSV for analysis

### Latency Optimization
- **Embedding caching**: Cache query embeddings for repeated/similar queries
- **Connection pooling**: Keep persistent connections to vector DB
- **Async pipeline**: STT → embedding and retrieval in parallel where possible
- **Streaming LLM**: Start speaking TTS before full answer is generated

---

## 10. Deployment

### Platform: Hugging Face Spaces (Gradio SDK)
- **URL**: `https://huggingface.co/spaces/<team>/ultron-v`
- **SDK**: Gradio
- **Hardware**: Free CPU (2 vCPU, 16 GB RAM)
- **Always-on**: Yes (no cold starts)
- **Secrets**: Store API keys as HF Space secrets

### Environment Variables
```env
# STT
SARVAM_API_KEY=xxx

# LLM Providers
GROQ_API_KEY=xxx
CEREBRAS_API_KEY=xxx
SAMBANOVA_API_KEY=xxx
GOOGLE_API_KEY=xxx
TOGETHER_API_KEY=xxx
OPENROUTER_API_KEY=xxx

# Embeddings
VOYAGE_API_KEY=xxx
JINA_API_KEY=xxx

# Vector DB
QDRANT_URL=xxx
QDRANT_API_KEY=xxx
PINECONE_API_KEY=xxx
PINECONE_INDEX_HOST=xxx

# TTS
ELEVENLABS_API_KEY=xxx
```

---

## 11. Tech Stack Summary

| Component | Technology | Free Tier |
|-----------|-----------|-----------|
| **Language** | Python 3.11+ | — |
| **Framework** | FastAPI (backend logic) + Gradio (UI) | — |
| **STT** | Sarvam AI `saaras:v3` | ₹100 credits (~200 min) |
| **Embedding** | Voyage AI `voyage-multilingual-2` + Gemini backup | 50M tokens + unlimited |
| **Vector DB** | Qdrant Cloud + Pinecone backup | 4GB + 2GB |
| **LLM** | Groq → Cerebras → SambaNova → Gemini → Together → OpenRouter | All free |
| **TTS** | `edge-tts` + Sarvam + ElevenLabs | Unlimited + ₹100 + 10K chars |
| **Deployment** | Hugging Face Spaces | Free |
| **Orchestration** | LiteLLM (provider routing) + Instructor (structured output) | — |
| **Guardrails** | Custom (Pydantic validation + LLM-based checks) | — |
