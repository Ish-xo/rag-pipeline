# ULTRON-V — Implementation Plan

> **Submission Deadline**: August 22, 2026, 11:59 PM

---

## Phase 0: Setup & Data Preparation

### 0.1 Project Scaffolding
- [ ] Set up clean project structure (see directory layout below)
- [ ] Create `.env` with all API keys (see `account_setup.md`)
- [ ] Set up `pyproject.toml` or `requirements.txt` with pinned dependencies
- [ ] Configure `litellm` with all 6 LLM providers
- [ ] Test connectivity to all external services (Sarvam, ElevenLabs, Groq, Qdrant, Voyage, etc.)

### 0.2 Dataset Acquisition & Exploration
- [ ] Load MSMARCO-XI Hindi subset using **streaming mode** to avoid downloading the full 55 GB dataset
  ```python
  from datasets import load_dataset
  ds = load_dataset("ai4bharat/MSMARCO-XI", "hi", split="train", streaming=True)
  ```
- [ ] Explore data structure: count unique passages, analyze passage lengths, check query types
- [ ] Determine optimal subset size (target: ~100K unique passages from ~50K queries)
- [ ] Stream and extract only the data we need → save as local JSONL (~500 MB)

> **Dataset download strategy**: We do NOT download the full 55 GB dataset. We use HuggingFace streaming to iterate through the Hindi subset (~4 GB) and extract only unique passages into a local JSONL file. This is a **one-time local operation** — the deployed app never needs the raw dataset, only the pre-built vector index in Qdrant/Pinecone.

### 0.3 Data Processing Pipeline
- [ ] Deduplicate passages across queries (many queries share the same passages)
- [ ] Clean text: normalize unicode, remove HTML artifacts, trim whitespace
- [ ] Build passage registry: `passage_id → {english_text, hindi_text, metadata}`
- [ ] Export clean passages as JSONL for embedding

---

## Phase 1: Embedding & Indexing

### 1.1 Embedding Generation
- [ ] Set up Voyage AI client (`voyage-3`, 1024d)
- [ ] Set up Gemini embedding client as backup (`gemini-embedding-001`, 768d)
- [ ] Batch embed all ~100K English passages via Voyage AI
  - Batch size: 128 passages per request
  - Rate: 2,000 RPM → ~16 batches/sec → ~100K passages in ~15 min
  - Token budget: ~100K × 80 tokens = ~8M tokens (4% of Voyage's 200M free)
- [ ] Save embeddings locally as `.npy` files (backup before uploading)
- [ ] Build embedding ID → passage metadata mapping

### 1.2 Vector Database Setup
- [ ] Create Qdrant Cloud free cluster
- [ ] Create collection `ultron_passages` with schema (see `technical_details.md`)
- [ ] Configure scalar quantization (int8) for memory efficiency
- [ ] Batch upload vectors + payloads to Qdrant
- [ ] Verify with test queries
- [ ] Set up Pinecone as backup:
  - Create serverless index (1024d, cosine)
  - Upload same vectors
- [ ] Implement keep-alive cron for Qdrant (prevent 7-day inactivity suspension)

### 1.3 Chunking Strategies Implementation
- [ ] **Strategy 1**: Passage-level (base) — already done via dataset structure
- [ ] **Strategy 2**: Sliding window (256 tok, 64 overlap) — for passages > 200 tokens
- [ ] **Strategy 3**: Semantic chunking — merge adjacent similar passages
- [ ] **Strategy 4**: Metadata enrichment — attach query_type, is_selected, etc.
- [ ] Store `chunk_strategy` in metadata for analytics/comparison
- [ ] Write chunking strategy selector (configurable per query or ensemble)

---

## Phase 2: RAG Pipeline Core

### 2.1 Query Processing Module
- [ ] Language detection (from STT or via fasttext/langdetect)
- [ ] Query translation: if Hindi → translate to English for retrieval (using Sarvam `translate` mode or LLM)
- [ ] Query expansion: generate 2-3 query variants for broader retrieval
- [ ] HyDE (Hypothetical Document Embedding): generate hypothetical answer, embed it

### 2.2 Retrieval Module
- [ ] Implement Qdrant search client (with fallback to Pinecone)
- [ ] Top-K retrieval (k=10 initially, configurable)
- [ ] Payload filtering (by language, query_type if applicable)
- [ ] Re-ranking: use cosine similarity threshold to filter weak matches
- [ ] Implement retrieval with multiple strategies:
  - Direct query embedding search
  - HyDE-enhanced search
  - Query expansion search (union of results)
- [ ] Reciprocal Rank Fusion (RRF) to merge results from multiple strategies
- [ ] Return top-5 passages with scores

### 2.3 LLM Answer Generation
- [ ] Implement LLM provider cascade (Groq → Cerebras → SambaNova → Gemini → Together → OpenRouter)
- [ ] Use `litellm` for unified API interface
- [ ] Use `instructor` for structured output (RAGResponse schema)
- [ ] System prompt design (see `prompts.md`)
- [ ] Implement streaming for TTFT optimization
- [ ] Token budget management: limit context to fit within model's window

### 2.4 Model Harness
- [ ] Pydantic schemas for all inputs/outputs (RAGQuery, RAGResponse, SourceCitation)
- [ ] Retry logic with exponential backoff + jitter
- [ ] Provider circuit breaker (disable after 3 consecutive failures)
- [ ] Timeout handling (5s per LLM call, 10s total)
- [ ] Request/response logging for debugging
- [ ] Error classification (rate_limit, timeout, server_error, invalid_response)

### 2.5 Guardrails
- [ ] **Input guardrails**:
  - Empty/short query rejection (< 3 words)
  - Toxicity filter (keyword list + LLM check for edge cases)
  - Language support check
- [ ] **Retrieval guardrails**:
  - Relevance threshold (cosine < 0.4 → "No relevant information found")
  - Passage diversity check
- [ ] **Output guardrails**:
  - Grounding check (verify answer references retrieved passages)
  - Confidence scoring
  - Refusal for off-topic, unsafe, or ungrounded responses
- [ ] Guardrail bypass for evaluation/testing mode

---

## Phase 3: STT, TTS & Frontend Integration

### 3.1 STT Integration
- [ ] Sarvam STT client (primary)
  - Handle audio format conversion (wav/mp3 at 16kHz)
  - Send to `/speech-to-text` endpoint
  - Parse transcript + language detection
  - Handle errors (empty audio, too long, etc.)
- [ ] ElevenLabs Scribe STT client (backup)
  - `scribe_v2` model
  - Hindi + English support
  - Word-level timestamps
- [ ] STT failover logic: Sarvam → ElevenLabs → text input fallback

### 3.2 TTS Integration
- [ ] `edge-tts` async client (primary)
  - Auto-select voice based on detected language
  - Hindi: `hi-IN-SwaraNeural` / `hi-IN-MadhurNeural`
  - English: `en-IN-NeerjaNeural` / `en-IN-PrabhatNeural`
- [ ] Sarvam TTS client (secondary)
  - `bulbul:v3` model
  - Handle 2,500 char limit (split long answers)
- [ ] ElevenLabs TTS client (tertiary, for polish)
- [ ] TTS provider selection based on availability/quality preference

### 3.3 Gradio UI
- [ ] Main interface: Audio input (microphone) + Text input (optional)
- [ ] Custom theme: Ultron dark theme (dark background, red/crimson accents)
- [ ] Components:
  - Audio recorder (Gradio `gr.Audio`)
  - Text display for transcript
  - Answer display with source citations (collapsible)
  - Audio player for TTS response
  - Language selector (English / Hindi)
  - Latency breakdown display (STT, retrieval, generation, TTS)
- [ ] Settings panel:
  - TTS voice selection
  - Number of sources to show
  - Chunking strategy toggle (for demo purposes)

### 3.4 End-to-End Pipeline Wiring
- [ ] Wire: Audio → STT → Query Processing → Retrieval → Generation → TTS → Audio
- [ ] Handle async flow (non-blocking UI)
- [ ] Progress indicators during processing
- [ ] Error handling at each stage with user-friendly messages

---

## Phase 4: Latency Benchmarking

### 4.1 Benchmark Script
- [ ] Select 100+ test queries from MSMARCO-XI validation set
- [ ] For each query:
  - Record timestamps at each pipeline stage (T0-T6)
  - Log: STT latency, embedding latency, retrieval latency, TTFT, total generation, TTS latency
- [ ] Calculate P50, P70, P100 for each metric
- [ ] Output results as CSV + summary table

### 4.2 Latency Optimization
- [ ] Profile bottlenecks
- [ ] Implement query embedding cache (LRU cache)
- [ ] Connection pooling for vector DB
- [ ] Optimize Gradio event handlers (avoid redundant processing)
- [ ] Test with different LLM providers, pick fastest for demo

### 4.3 Analytics Dashboard
- [ ] Add latency breakdown to Gradio UI
- [ ] Show per-query timing: STT | Retrieval | Generation | TTS
- [ ] Show aggregate P50/P70/P100 stats
- [ ] Export analytics as downloadable CSV

---

## Phase 5: Polish, Deploy & Submit

### 5.1 Deployment to HF Spaces
- [ ] Create Hugging Face Space (`ultron-v`, Gradio SDK)
- [ ] Upload code and `requirements.txt`
- [ ] Set API keys as Space secrets
- [ ] Test live deployment end-to-end
- [ ] Verify all providers work from HF Spaces IP

### 5.2 README & Documentation
- [ ] Write comprehensive README.md:
  - Project overview, architecture diagram
  - Setup instructions (local + deployment)
  - API keys needed
  - Demo video embed
  - Latency results table
  - Chunking strategies explanation
  - Tech stack
- [ ] Code documentation (docstrings, type hints)

### 5.3 Testing
- [ ] Test with Hindi voice queries
- [ ] Test with English voice queries  
- [ ] Test with edge cases:
  - Very short queries ("hello")
  - Off-topic queries ("what's the weather?")
  - Inappropriate queries
  - Very long queries
  - Mixed language (Hinglish)
  - No audio (empty submission)
- [ ] Test guardrail responses
- [ ] Test provider failover (temporarily disable primary)

### 5.4 Videos
- [ ] **Video 1** (90s): Team process video
  - Show team collaboration (screen shares, discussions)
  - Show planning artifacts, whiteboard sketches
  - Show coding in progress
- [ ] **Video 2**: Demo video
  - Show end-to-end: speak a question → get answer + audio
  - Show Hindi and English queries
  - Show guardrails in action (off-topic rejection)
  - Show latency analytics
  - Show multiple chunking strategies
- [ ] Upload to Instagram, X, LinkedIn (all 3 members)
- [ ] Include `#RAGInGoa` in every post

### 5.5 Submission
- [ ] Verify GitHub repo is public and clean
- [ ] Verify HF Space is live and working
- [ ] Fill submission form: https://forms.gle/MNvCjcv23Hn2Eeu58
- [ ] Double-check all social media posts are up
- [ ] At least 1 Instagram account is public

---

## Directory Structure

```
rag-pipeline/
├── README.md
├── requirements.txt
├── .env.example
├── .env                          # (gitignored)
├── app.py                        # Gradio UI entry point (for HF Spaces)
├── artifacts/                    # Planning documents
│   ├── project_details.md
│   ├── technical_details.md
│   ├── implmentation_plan.md
│   ├── api_reference.md
│   ├── account_setup.md
│   ├── prompts.md
│   └── latency_results.md
├── src/
│   ├── __init__.py
│   ├── config.py                 # Environment variables, constants
│   ├── pipeline.py               # End-to-end pipeline orchestrator
│   │
│   ├── stt/                      # Speech-to-Text
│   │   ├── __init__.py
│   │   ├── sarvam_client.py
│   │   ├── elevenlabs_client.py
│   │   └── base.py               # STT interface
│   │
│   ├── tts/                      # Text-to-Speech
│   │   ├── __init__.py
│   │   ├── edge_tts_client.py
│   │   ├── sarvam_tts_client.py
│   │   ├── elevenlabs_client.py
│   │   └── base.py               # TTS interface
│   │
│   ├── embeddings/               # Embedding generation
│   │   ├── __init__.py
│   │   ├── voyage_client.py
│   │   ├── gemini_client.py
│   │   ├── jina_client.py
│   │   └── base.py               # Embedding interface
│   │
│   ├── retrieval/                # Vector search & retrieval
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   ├── pinecone_client.py
│   │   ├── retriever.py          # Retrieval orchestration (RRF, HyDE)
│   │   └── base.py               # Retriever interface
│   │
│   ├── chunking/                 # Chunking strategies
│   │   ├── __init__.py
│   │   ├── passage_chunker.py    # Strategy 1: passage-level
│   │   ├── sliding_window.py     # Strategy 2: sliding window
│   │   ├── semantic_chunker.py   # Strategy 3: semantic grouping
│   │   └── base.py               # Chunker interface
│   │
│   ├── llm/                      # LLM answer generation
│   │   ├── __init__.py
│   │   ├── provider_cascade.py   # Multi-provider failover
│   │   ├── harness.py            # Model harness (retries, structured I/O)
│   │   ├── prompts.py            # System/user prompt templates
│   │   └── schemas.py            # Pydantic schemas (RAGQuery, RAGResponse)
│   │
│   ├── guardrails/               # Safety & quality checks
│   │   ├── __init__.py
│   │   ├── input_guard.py        # Pre-retrieval checks
│   │   ├── retrieval_guard.py    # Post-retrieval checks
│   │   ├── output_guard.py       # Post-generation checks
│   │   └── schemas.py            # GuardrailResult schema
│   │
│   └── analytics/                # Latency tracking
│       ├── __init__.py
│       ├── timer.py              # Pipeline stage timer
│       ├── reporter.py           # P50/P70/P100 calculator
│       └── dashboard.py          # Gradio analytics components
│
├── scripts/
│   ├── prepare_dataset.py        # Stream MSMARCO-XI, extract & deduplicate passages
│   ├── embed_passages.py         # Batch embed passages
│   ├── upload_vectors.py         # Upload to Qdrant/Pinecone
│   ├── benchmark.py              # Run latency benchmarks
│   └── test_providers.py         # Test all API provider connectivity
│
├── data/                         # (gitignored) Local data cache
│   ├── passages_clean.jsonl
│   ├── embeddings/
│   └── benchmarks/
│
└── tests/
    ├── test_stt.py
    ├── test_retrieval.py
    ├── test_generation.py
    ├── test_guardrails.py
    └── test_pipeline.py
```

---

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Sarvam STT rate limit hit | Can't process voice input | Failover to ElevenLabs Scribe; offer text input fallback |
| All LLM providers rate-limited simultaneously | No answer generation | Return raw retrieved passages as answer |
| Qdrant 7-day inactivity deletion | Lose all indexed data | Keep-alive cron + Pinecone backup |
| Voyage AI token quota exhausted | Can't embed new queries | Switch to Gemini embeddings at query time |
| HF Spaces downtime | Live link broken | Have backup deployment ready (Render/Railway) |
| 200ms latency impossible for full pipeline | Poor benchmark numbers | Separate retrieval latency from generation, report both clearly |
| ElevenLabs shared credits exhausted | STT backup + TTS unavailable | Use edge-tts for TTS, text input for STT |

---

## Key Dependencies

```
# Core
fastapi>=0.104.0
gradio>=5.0.0
pydantic>=2.0
python-dotenv
httpx
aiohttp

# LLM
litellm>=1.40.0
instructor>=1.0.0
openai>=1.0.0
google-genai

# Embeddings
voyageai

# Vector DB
qdrant-client>=1.7.0
pinecone-client>=3.0.0

# STT/TTS
sarvamai
elevenlabs
edge-tts

# Data Processing
datasets  # HuggingFace datasets
pandas
numpy

# Analytics
tabulate

# Utilities
tenacity  # retry logic
```
