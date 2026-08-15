# ULTRON-V — Technical Architecture

## System Overview

### Default Pipeline (Fast Path — latency-optimized)

```
🎤 Audio
   ↓
┌──────────────┐
│  STT         │  Sarvam saaras:v3 (primary) → ElevenLabs scribe_v2 (backup)
└──────┬───────┘
       ↓
┌──────────────┐
│  Input Guard │  safety/topic filter (deterministic, <5ms)
└──────┬───────┘
       ↓
┌──────────────┐
│  Embedding   │  Voyage AI voyage-3 (1024d)
└──────┬───────┘
       ↓
┌──────────────┐
│  Qdrant      │  Top-K vector search (1024d collection)
└──────┬───────┘
       ↓
┌──────────────┐
│  Reranker    │  cosine threshold + diversity filter (deterministic, <5ms)
└──────┬───────┘
       ↓
┌──────────────┐
│  LLM Harness │  Sequential failover: Groq → Cerebras → Gemini (Core 3)
└──────┬───────┘
       ↓
┌──────────────┐
│  Grounding   │  Tier 1 deterministic check (<5ms) → Tier 2 LLM verifier (if ambiguous)
└──────┬───────┘
       ↓
┌──────────────┐
│  edge-tts    │  TTS (hi-IN-SwaraNeural / en-IN-NeerjaNeural)
└──────┬───────┘
       ↓
     🔊
```

### Quality Path (accuracy-optimized, opt-in)

```
STT → Input Guard → [Query Expansion + HyDE + Direct Embedding]
                                    ↓
                          [3× parallel Qdrant search]
                                    ↓
                              [RRF Fusion]
                                    ↓
                           [LLM Harness → Grounding → TTS]
```

> **Design philosophy**: Simple default pipeline + sophisticated optional retrieval. The fast path is the demo default. The quality path is an experimental mode that shows we can do more. Both are benchmarked and compared.

---

## 1. Speech-to-Text (STT)

### Primary: Sarvam AI (`saaras:v3`)
- **Endpoint**: `POST https://api.sarvam.ai/speech-to-text`
- **Free Credits**: ₹100 on signup (~200 minutes of audio)
- **Rate Limit**: 60 RPM
- **Max Audio Length**: 30 seconds per request (REST API)
- **Languages**: Hindi (`hi-IN`), English (`en-IN`), auto-detect
- **Key Features**: 
  - `mode=transcribe` — verbatim transcription
  - `mode=translate` — Indic speech → English text (useful for cross-lingual retrieval)
  - `mode=codemix` — Hinglish support
  - Auto language detection when `language_code` omitted
- **Auth**: `api-subscription-key` header

### Backup: ElevenLabs Scribe (`scribe_v2`)
- **Endpoint**: `POST https://api.elevenlabs.io/v1/speech-to-text`
- **Free Tier**: 10,000 credits/month (shared with TTS)
- **Concurrency**: 8 concurrent requests on free tier
- **Languages**: 90+ languages including Hindi + 10 Indic languages
- **Key Features**: Speaker diarization, word-level timestamps, code-switching
- **Auth**: `xi-api-key` header

### Failover: Sarvam (`saaras:v3`) → ElevenLabs (`scribe_v2`) → text input prompt

---

## 2. Chunking Strategies & Production Strategy Selection

> **Task requirement**: *"Chunking strategy should be vast — don't submit a single naive fixed-size chunking approach."*

The MSMARCO-XI dataset contains **~10 passages per query**. Each passage is a self-contained text unit (~60-80 words). These are independently sourced web passages grouped by query relevance, not sequential pages of a single document.

### Experimental Chunking Strategies (Benchmarked in Isolated Collections)
1. **Strategy 1: Native Passage-Level (Base)**
   - Each passage = one retrieval unit (~60-80 words)
   - Preserves original MS MARCO semantic boundaries
   - Metadata: `query_id`, `query_type`, `is_selected`, `language`
2. **Strategy 2: Fixed Token Window**
   - Split passages into fixed 128-token windows without overlap
   - Baseline strategy for token-budget comparison
3. **Strategy 3: Sliding Window with Overlap**
   - 256 token windows with 64 token overlap
   - Parent-child tracking: each sub-chunk references its parent passage
4. **Strategy 4: Semantic Sentence Grouping**
   - Group sentences within a single passage by semantic similarity
   - Split at topic transitions within a passage (never merge across unrelated passages)
5. **Strategy 5: Parent-Child Hierarchical**
   - Index sentence-level child chunks for high precision
   - Return parent passage as context for LLM generation

### Production Selection Rule
- All 5 strategies are evaluated experimentally on a held-out development set using temporary collections.
- **We do NOT deploy all 5 strategies simultaneously in production.**
- After benchmarking, the single best-performing chunking strategy (highest Recall@5 / NDCG@5 with minimal retrieval latency overhead) is selected and indexed into the final production Qdrant collection.

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

## 3. Retrieval Strategies (Separate from Chunking)

### Strategy 1: Dense Direct Retrieval (DEFAULT — Fast Path)
- Embed query → Qdrant top-K search → return passages
- Lowest latency path (~50-100ms total retrieval)

### Strategy 2: Query Expansion (Quality Path)
- Generate 2-3 query variants via LLM
- Run parallel vector searches for each variant
- Merge results using RRF

### Strategy 3: HyDE — Hypothetical Document Embedding (Quality Path)
- Generate hypothetical answer via LLM
- Embed hypothetical answer and search
- Better for complex or ambiguous queries

### Strategy 4: Ensemble + RRF (Quality Path)
- Run direct + expanded + HyDE searches in parallel
- Merge using Reciprocal Rank Fusion
- Re-rank by cosine similarity threshold

> **Critical**: HyDE and query expansion add an LLM call BEFORE retrieval. This is **only used in the opt-in quality path**, never in the default fast path.

---

## 4. Embedding & Fallback Architecture

### Canonical Configuration

| Role | Provider | Model | Dimensions | Free Quota |
|------|----------|-------|------------|------------|
| **Primary** | Voyage AI | `voyage-3` | 1024 | 200M tokens |
| **Backup 1** | Google Gemini | `gemini-embedding-001` | 768 | Unlimited (Free Tier) |
| **Backup 2 (Stretch)** | Jina AI | `jina-embeddings-v4` | 1024 | 10M tokens |

### Embedding Dimension Isolation Rule
- **Primary Collection**: `ultron_passages_voyage_1024` (1024 dimensions, Cosine distance).
- **Fallback Collection**: `ultron_passages_gemini_768` (768 dimensions, Cosine distance).
- ⚠️ **STRICT PROHIBITION**: A 768d vector from Gemini must NEVER be queried against a 1024d Voyage collection. Vectors must NEVER be padded, truncated, or resized across dimensions.
- If Voyage AI is unavailable at query time, Gemini fallback is only activated if the corresponding `ultron_passages_gemini_768` collection has been indexed. Otherwise, the system fails over to a secondary 1024d provider (Jina AI `jina-embeddings-v4` which matches the 1024d space, or returns cached results).

### Incremental Embedding Strategy
- **Dataset Size Experiment (10K → 50K → 100K)**:
  - First, embed 10,000 unique passages → save to `data/embeddings/voyage_10k.npy`.
  - Next, embed the additional 40,000 unique passages → concatenate with 10k to form 50k (`data/embeddings/voyage_50k.npy`).
  - Next, embed the remaining 50,000 unique passages → concatenate to form 100k (`data/embeddings/voyage_100k.npy`).
  - **No passage is ever embedded twice.**

### Indexing Language Experiment
- Compare 4 configurations on a 10K sample to empirically validate the best approach:
  1. English index + English queries
  2. Hindi index + Hindi queries
  3. English index + Hindi queries (cross-lingual)
  4. Dual English + Hindi index + Hindi queries

---

## 5. Vector Database

### Primary: Qdrant Cloud (Free Tier)
- **Storage**: 4 GB disk, 1 GB RAM, 0.5 vCPU
- **Capacity**: ~500K vectors at 1024d (uncompressed), ~1M with scalar quantization
- **Features**: HNSW index, payload filtering, scalar quantization (int8)
- **Inactivity Policy**: Suspended after 7 days idle → keep-alive cron

### Backup: Pinecone Serverless (Free Tier)
- **Storage**: 2 GB, ~250K-300K vectors at 1024d
- **Rate Limits**: 2M WU/mo, 1M RU/mo
- **Region**: AWS us-east-1 only

### Primary Collection Design
```
Collection: ultron_passages_voyage_1024
├── Vectors: 1024d (Voyage voyage-3)
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

---

## 6. LLM — Answer Generation

### Latency Strategy & Confirmed Measurement Scope

The task specifies an end-to-end latency target (<200ms). It is confirmed that **latency calculation begins after STT is complete (when query text is ready at T1) through to when output is provided**:
- **Official Evaluation Scope (Post-STT End-to-End)**: Covers Input Guardrails → Query Embedding → Qdrant Vector Search → Reranking → LLM Generation / First Token.
- **Retrieval Latency (T5 - T2)**: Targeted at **<100ms** (Voyage-3 embedding + Qdrant 1024d search + reranker).
- **Time to First Useful Output / TTFT (T6 - T1)**: Targeted at **<200ms** utilizing Groq LPUs (`llama-3.3-70b-versatile`) with streaming token delivery.
- **Full Text Generation & TTS Playback**: Measured and reported transparently in benchmark logs to provide complete latency visibility.

### Canonical Provider Configuration

All providers are used in **sequential failover order**, NOT called simultaneously for normal requests.

#### Core Providers (Always Configured & Tested)
| Priority | Provider | Model Name | Format | TTFT (P50) | Free Limits |
|:---:|---|---|---|---|---|
| **1 (Primary)** | **Groq** | `llama-3.3-70b-versatile` | OpenAI-compatible | ~120-180ms | 30 RPM, 14.4k RPD |
| **2 (Backup 1)** | **Cerebras** | `llama-3.3-70b` | OpenAI-compatible | ~150-250ms | 30 RPM, 1M tokens/day |
| **3 (Backup 2)** | **Google Gemini** | `gemini-2.5-flash` | Google GenAI SDK | ~250-450ms | 15 RPM, 1,500 RPD |

#### Stretch Providers (Integrated if Time Permits)
| Priority | Provider | Model Name | Format | Free Limits |
|:---:|---|---|---|---|
| **4 (Stretch)** | **SambaNova** | `Meta-Llama-3.3-70B-Instruct` | OpenAI-compatible | 240 RPM, 48k RPD |
| **5 (Stretch)** | **Together AI** | `meta-llama/Llama-3.3-70B-Instruct-Turbo` | OpenAI-compatible | $5 signup credits |
| **6 (Stretch)** | **OpenRouter** | `google/gemini-2.5-flash:free` | OpenAI-compatible | 20 RPM, 50 RPD |

### Failover Execution Flow
```python
core_providers = [
    ("groq", "llama-3.3-70b-versatile"),
    ("cerebras", "llama-3.3-70b"),
    ("gemini", "gemini-2.5-flash")
]

for provider_name, model_id in core_providers:
    try:
        response = await invoke_llm(provider_name, model_id, prompt, timeout=5.0)
        return response
    except (RateLimitError, TimeoutError, APIError) as e:
        logger.warning(f"Provider {provider_name} failed: {e}. Failing over to next provider.")
        continue

raise ProviderExhaustedError("Answer generation is temporarily unavailable.")
```

---

## 7. Model Harness

### Harness Components

#### A. Structured Input/Output (via Pydantic + Instructor)
```python
class RAGQuery(BaseModel):
    query_text: str
    language: str
    original_audio_duration: float
    
class SourceCitation(BaseModel):
    passage_text: str
    passage_id: str
    relevance_score: float

class RAGResponse(BaseModel):
    answer: str
    confidence: float  # 0.0 - 1.0
    sources: list[SourceCitation]
    is_grounded: bool
    language: str
```

#### B. Robust Failover & Circuit Breaker
- Exponential backoff with jitter on transient failures.
- Circuit breaker: Provider is temporarily disabled after 3 consecutive failures and re-probed after 60s cooldown.
- Timeout handling: 5s per LLM call, 10s total pipeline timeout.

#### C. Error Recovery
- If all LLM providers are rate-limited or fail: Return a clean status message (*"Answer generation is temporarily unavailable."*) while safely exposing the top retrieved source passages in a collapsible UI drawer.

---

## 8. Guardrails

### Layer 1: Input Guardrails (Pre-Retrieval, Deterministic, <5ms)
- Empty / noise audio detection (transcripts < 3 words rejected).
- Language support validation.
- Toxicity / injection blocklist (regex pattern matching, zero LLM latency).

### Layer 2: Retrieval Guardrails (Post-Retrieval, Deterministic, <5ms)
- Relevance threshold: If top passage cosine similarity < 0.40 → return polite out-of-domain response.
- Source diversity check: Prevent all passages from originating from a single duplicated query ID.

### Layer 3: Two-Tier Output Grounding Check

```
Generated Answer + Context Passages
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ Tier 1: Deterministic Suspicion Check (<5ms)           │
│ - Validate citation tags exist in retrieved passages   │
│ - Check named entity presence in cited passages        │
│ - Match key noun phrases / factual numbers             │
└────────────────────────┬───────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
[Clear Verdict]                  [Ambiguous / Suspicious]
(High match & valid citations)   (Mismatch in numbers/entities)
        │                                 │
        ▼                                 ▼
 Mark GROUNDED or UNGROUNDED     ┌────────────────────────────────┐
                                 │ Tier 2: LLM Verifier (~10%)    │
                                 │ Fast verification prompt       │
                                 └────────────────────────────────┘
```

> **Design rule**: Token overlap alone is NOT treated as proof of factual grounding (it is merely a heuristic filter). Only ambiguous cases trigger a Tier 2 LLM verifier, preserving low latency for the fast path.

---

## 9. Text-to-Speech (TTS)

### Primary: `edge-tts` (Unlimited Free, Async)
- Hindi: `hi-IN-SwaraNeural` (Female), `hi-IN-MadhurNeural` (Male)
- English: `en-IN-NeerjaNeural` (Female), `en-IN-PrabhatNeural` (Male)
- High naturalness, zero API key requirement, async execution.

### Backup: Sarvam TTS (`bulbul:v3`)
- Native Indic intonation, used for Hindi showcase.

### Tertiary: ElevenLabs (`eleven_multilingual_v2`)
- Reserved for final video presentation and demo polish.

---

## 10. Latency Analytics & Benchmark Structure

### Granular Measurement Stages
```
T0: Audio received at server
T1: STT transcript ready                    ← OFFICIAL BENCHMARK START
T2: Input guardrail validation complete
T3: Query embedding vector generated
T4: Qdrant vector search complete
T5: Retrieval guardrails & reranking complete (Retrieval Latency: T5 - T2, Target: <100ms)
T6: LLM Time to First Token (TTFT)          ← OFFICIAL PRIMARY TARGET (<200ms from T1)
T7: Full LLM text generation complete
T8: Output grounding check complete         ← FULL POST-STT VALIDATED OUTPUT
T9: TTS audio generation complete           ← COMPLETE AUDIO PLAYBACK READY

Official & Instrument Metrics:
1. Post-STT Time to First Output / TTFT (T6 - T1): PRIMARY CHALLENGE TARGET (<200ms)
2. Retrieval Latency (T5 - T2): Primary Retrieval Target (<100ms)
3. Full Post-STT Validated Answer (T8 - T1): Measured & logged
4. Full Audio End-to-End Pipeline (T9 - T0): Total voice interaction latency
```

### Dataset Split & Leakage Prevention
- MSMARCO-XI (`hi`) provides `train` split data.
- **Split Verification**: If a dedicated `validation` split is not available on Hugging Face, a **deterministic held-out evaluation set** is created by hashing `query_id` with a fixed seed (e.g. 50 dev queries for tuning, 100 test queries for final benchmarks).
- **Leakage Prevention**: All passages and queries belonging to the dev and test sets are strictly removed from the indexing corpus before generating production embeddings.

---

## 11. Deployment

### Platform: Hugging Face Spaces (Gradio SDK)
- **URL**: `https://huggingface.co/spaces/<team>/ultron-v`
- **Hardware**: Free Tier CPU (2 vCPU, 16 GB RAM)
- **Always-on**: Zero cold start.
- **Data independence**: Deployment does not host raw 55GB dataset files; it connects directly to Qdrant Cloud.

### Environment Variables (.env)
```env
# === STT ===
SARVAM_API_KEY=
ELEVENLABS_API_KEY=

# === Core LLM Providers ===
GROQ_API_KEY=
CEREBRAS_API_KEY=
GOOGLE_API_KEY=

# === Stretch LLM Providers ===
SAMBANOVA_API_KEY=
TOGETHER_API_KEY=
OPENROUTER_API_KEY=

# === Embeddings ===
VOYAGE_API_KEY=

# === Vector DB ===
QDRANT_URL=
QDRANT_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_HOST=

# === Deployment ===
HF_TOKEN=
```

---

## 12. Tech Stack Summary

| Component | Technology | Canonical Model / Details |
|---|---|---|
| **STT Primary** | Sarvam AI | `saaras:v3` |
| **STT Backup** | ElevenLabs | `scribe_v2` |
| **Embedding Primary** | Voyage AI | `voyage-3` (1024d) |
| **Embedding Backup** | Google Gemini | `gemini-embedding-001` (768d, separate collection) |
| **Vector DB Primary** | Qdrant Cloud | Collection `ultron_passages_voyage_1024` |
| **Vector DB Backup** | Pinecone Serverless | Cosine index (1024d) |
| **LLM Core 1** | Groq | `llama-3.3-70b-versatile` |
| **LLM Core 2** | Cerebras | `llama-3.3-70b` |
| **LLM Core 3** | Google Gemini | `gemini-2.5-flash` |
| **LLM Stretch** | SambaNova / Together / OpenRouter | `Meta-Llama-3.3-70B-Instruct` / Turbo / Flash |
| **TTS Primary** | `edge-tts` | `hi-IN-SwaraNeural` / `en-IN-NeerjaNeural` |
| **TTS Backup** | Sarvam AI | `bulbul:v3` |
| **UI & Hosting** | Gradio | Hugging Face Spaces |
