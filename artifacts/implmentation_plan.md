# ULTRON-V — Implementation Plan

> **Submission Deadline**: August 22, 2026, 11:59 PM

---

## Phase 0: Setup & Account Verification

### 0.1 Project Scaffolding
- [ ] Initialize repository structure with modular components (see directory layout below)
- [ ] Configure `.env` from template with verified API keys
- [ ] Pin exact dependencies in `requirements.txt`
- [ ] Configure `litellm` router for sequential failover across Core 3 LLM providers
- [ ] Run `scripts/test_providers.py` to verify network and credentials for all active APIs

### 0.2 Account & Key Checklist
- [ ] Sarvam AI (`SARVAM_API_KEY`)
- [ ] ElevenLabs (`ELEVENLABS_API_KEY`)
- [ ] Groq (`GROQ_API_KEY`)
- [ ] Cerebras (`CEREBRAS_API_KEY`)
- [ ] Google AI Studio (`GOOGLE_API_KEY`)
- [ ] Voyage AI (`VOYAGE_API_KEY`)
- [ ] Qdrant Cloud (`QDRANT_URL`, `QDRANT_API_KEY`)
- [ ] Pinecone (`PINECONE_API_KEY`, `PINECONE_INDEX_HOST`)
- [ ] Hugging Face (`HF_TOKEN`)

---

## Phase 1: Data Processing & Controlled Experiments

### 1.1 Dataset Streaming & Split Construction
- [ ] Stream `ai4bharat/MSMARCO-XI` (`hi`) without downloading the 55 GB full multi-language dataset
  ```python
  from datasets import load_dataset
  ds = load_dataset("ai4bharat/MSMARCO-XI", "hi", split="train", streaming=True)
  ```
- [ ] **Deterministic Split Construction (Zero Leakage)**:
  - Check whether a dedicated `validation` split exists on HF for the Hindi subset.
  - If only `train` split is available, partition deterministically using a fixed hash on `query_id`:
    - **Development Set (50 queries)**: Used strictly for parameter tuning, threshold calibration, and prompt refinement.
    - **Test Benchmark Set (100 queries)**: Held-out set reserved strictly for final reporting. Never tuned against.
    - **Corpus Index**: All passages associated with dev/test queries are segregated to avoid ground-truth contamination.
- [ ] Extract unique passages across training queries (deduplicating identical passages across query IDs).
- [ ] Clean text (unicode normalization, whitespace cleanup, HTML entity stripping).
- [ ] Save processed passages as local JSONL: `data/passages_clean.jsonl` (~500 MB).

### 1.2 Incremental Dataset Size Experiment
- [ ] **Objective**: Find the optimal index size balancing retrieval accuracy (Recall@5, NDCG@5) against storage and latency.
- [ ] **Incremental Embedding Strategy (Zero Redundant API Calls)**:
  1. Embed first 10,000 unique passages using Voyage AI `voyage-3` (1024d) → save to `data/embeddings/voyage_10k.npy`.
  2. Embed next 40,000 unique passages → concatenate with 10k to create 50k corpus (`data/embeddings/voyage_50k.npy`).
  3. Embed next 50,000 unique passages → concatenate to create 100k corpus (`data/embeddings/voyage_100k.npy`).
- [ ] Benchmark each subset in isolated Qdrant test collections against the 50-query dev set.
- [ ] Select the smallest corpus size meeting retrieval quality thresholds.

### 1.3 Indexing Language Experiment
- [ ] Evaluate 4 indexing configurations on a controlled 10K passage sample:
  - **Exp A**: English passages indexed, queried with English queries.
  - **Exp B**: Hindi translated passages indexed, queried with Hindi queries.
  - **Exp C**: English passages indexed, queried with Hindi queries (cross-lingual embedding capability).
  - **Exp D**: Dual English + Hindi passages indexed, queried with Hindi queries.
- [ ] Evaluate Recall@5 and NDCG@5 to select the empirically superior indexing approach.

---

## Phase 2: Production Embedding & Vector DB Setup

### 2.1 Production Embedding Generation
- [ ] Batch embed the selected production passage corpus using Voyage AI `voyage-3` (1024d, batch size: 128).
- [ ] Persist all embeddings locally as `.npy` backups before uploading to vector storage.
- [ ] (Optional) Embed passages with Gemini `gemini-embedding-001` (768d) ONLY if populating a separate `ultron_passages_gemini_768` collection for emergency embedding failover.

### 2.2 Vector Database Setup (Strict Dimensional Isolation)
- [ ] Provision Qdrant Cloud collection: `ultron_passages_voyage_1024` (1024d, Cosine distance, int8 Scalar Quantization).
- [ ] Batch upload vectors and full payload metadata (`chunk_id`, `text`, `english_text`, `translated_text`, `query_id`, `query_type`, `is_selected`).
- [ ] Configure Pinecone Serverless (1024d, Cosine) as secondary hot backup.
- [ ] Set up a lightweight keep-alive ping script to prevent Qdrant 7-day inactivity pause.

### 2.3 Chunking Strategy Benchmark & Single Production Strategy Selection
- [ ] Implement and evaluate 5 distinct chunking strategies in isolated test collections:
  1. **Native Passage-Level (Base)**: Passage as atomic unit (~60-80 words).
  2. **Fixed Token Window**: 128-token non-overlapping slices.
  3. **Sliding Window with Overlap**: 256 tokens with 64-token stride + parent tracking.
  4. **Semantic Sentence Grouping**: Topic-boundary splitting strictly within individual passages.
  5. **Parent-Child Hierarchical**: Sentence-level retrieval returning parent passage context.
- [ ] Measure Recall@5, NDCG@5, and retrieval latency for each on the dev set.
- [ ] **Production Rule**: Select the single highest-performing strategy and deploy ONLY that strategy to the production Qdrant collection.

---

## Phase 3: RAG Core & Sequential Model Harness

### 3.1 Retrieval Module
- [ ] **Fast Path (Default)**:
  - Query text → Voyage `voyage-3` (1024d) → Qdrant search → Cosine threshold filter (≥0.40) → Top-5 passages.
  - Target: <100ms retrieval latency.
- [ ] **Quality Path (Opt-in Ensemble)**:
  - Parallel generation: Direct Query + Query Expansion (2 variants) + HyDE hypothetical passage.
  - Multi-vector search with Reciprocal Rank Fusion (RRF).
- [ ] Reranker & Diversity Filter: Deduplicate passages sharing the same parent query ID.

### 3.2 Sequential LLM Failover Cascade
- [ ] Core Sequential Cascade:
  1. **Groq** (`llama-3.3-70b-versatile`) — Primary low-latency generation.
  2. **Cerebras** (`llama-3.3-70b`) — Backup generation.
  3. **Google Gemini** (`gemini-2.5-flash`) — Emergency fallback.
- [ ] Stretch Providers (if time permits): SambaNova (`Meta-Llama-3.3-70B-Instruct`), Together AI (`meta-llama/Llama-3.3-70B-Instruct-Turbo`), OpenRouter (`google/gemini-2.5-flash:free`).
- [ ] Streaming interface enabled to minimize Time to First Token (TTFT).

### 3.3 Model Harness & Resilience
- [ ] Pydantic / Instructor structured I/O validation (`RAGQuery`, `RAGResponse`, `SourceCitation`).
- [ ] Exponential backoff with jitter on HTTP 429/500 errors.
- [ ] Circuit breaker: Temporarily mute any provider encountering 3 consecutive errors (60s cooldown).
- [ ] Graceful Degradation: If all LLMs fail, return status message (*"Answer generation is temporarily unavailable."*) and expose retrieved sources in a collapsible UI drawer.

### 3.4 Two-Tier Grounding & Safety Guardrails
- [ ] **Input Guardrails (<5ms)**: Empty/noise audio filter (<3 words), language verification, regex injection/toxicity blocklist.
- [ ] **Retrieval Guardrails (<5ms)**: Cosine similarity cutoff (<0.40 → out-of-domain refusal), source diversity validation.
- [ ] **Output Grounding**:
  - **Tier 1 (Deterministic, <5ms)**: Verify citation IDs correspond to retrieved passages; match named entities and key noun phrases.
  - **Tier 2 (LLM Verifier, ~10% of cases)**: Trigger fast verification prompt only when Tier 1 detects ambiguous entity or factual discrepancies.
  - *Token overlap alone is never treated as proof of factual accuracy.*

---

## Phase 4: Voice Integration (STT & TTS) & Gradio UI

### 4.1 Speech-to-Text (STT)
- [ ] Sarvam AI `saaras:v3` primary client (supports Hindi, English, Hinglish, verbatim, and translate modes).
- [ ] ElevenLabs `scribe_v2` backup client with automatic failover.
- [ ] Fallback to direct text input if audio input is corrupted or APIs are unreachable.

### 4.2 Text-to-Speech (TTS)
- [ ] `edge-tts` async primary client (zero API key required, neural Hindi & English voices).
- [ ] Sarvam AI `bulbul:v3` backup client for native Indic pitch/prosody.
- [ ] ElevenLabs `eleven_multilingual_v2` for demo polish.

### 4.3 Gradio Application (`app.py`)
- [ ] Ultron dark aesthetic (dark metallic canvas, crimson/red accents, monospace data metrics).
- [ ] Audio recorder with live waveform + text input box.
- [ ] Structured response display: Streamed answer text, confidence badge, collapsible source citations, synthesized audio player.
- [ ] Mode switch toggle: Fast Path (Latency-First) vs Quality Path (Ensemble).
- [ ] Real-time latency waterfall breakdown displaying per-stage timings.

---

## Phase 5: Rigorous Benchmarking & Latency Instrumentation

### 5.1 Test Execution on Held-Out Benchmark Set
- [ ] Execute automated benchmark across the 100-query held-out test set using `scripts/benchmark.py`.
- [ ] Record exact timestamps for every stage:
  - T0: Audio received
  - T1: STT complete
  - T2: Input guardrails complete
  - T3: Query embedding complete
  - T4: Vector search complete
  - T5: Reranking / retrieval guardrails complete
  - T6: LLM Time to First Token (TTFT)
  - T7: Full LLM text generation complete
  - T8: Output grounding check complete
  - T9: TTS audio synthesis complete

### 5.2 Metric Computation & Reporting
- [ ] Compute P50, P70, and P100 for:
  - **Retrieval Latency** (T5 - T2, Target: <100ms)
  - **LLM TTFT** (T6 - T5, Optimization target: <200ms)
  - **Full LLM Generation** (T7 - T5)
  - **Post-STT End-to-End** (T8 - T1)
  - **Full End-to-End Pipeline** (T9 - T0)
- [ ] Benchmark comparison across Core LLM providers (Groq vs Cerebras vs Gemini).
- [ ] Compare Fast Path vs Quality Path retrieval quality (Recall@5, NDCG@5) and latency trade-offs.
- [ ] Populate all tables in `artifacts/latency_results.md` and export raw CSV data to `data/benchmarks/latency_results.csv`.

---

## Phase 6: Deployment, Documentation & Submission

### 6.1 Hugging Face Spaces Deployment
- [ ] Deploy repository to Hugging Face Spaces (Gradio SDK, CPU Free tier).
- [ ] Configure all API credentials securely in Space Secrets.
- [ ] Validate end-to-end functionality on live Space URL with live microphone input.

### 6.2 Documentation & Verification
- [ ] Comprehensive `README.md` with:
  - System architecture diagram
  - Experimental findings (dataset size, indexing language, chunking comparison)
  - Latency and quality benchmark tables (P50/P70/P100)
  - Local setup instructions and live HF Space link
- [ ] Complete codebase docstrings and type annotations.

### 6.3 Submission Deliverables
- [ ] Video 1 (90s): Team collaboration, planning artifacts, system design overview.
- [ ] Video 2: Live end-to-end working demo (Hindi + English voice queries, guardrail refusals, latency waterfall).
- [ ] Social media posts on Instagram, X, and LinkedIn by all team members including `#RAGInGoa`.
- [ ] Verify public visibility on at least 1 Instagram account.
- [ ] Submit official form before August 22, 2026, 11:59 PM: https://forms.gle/MNvCjcv23Hn2Eeu58

---

## Directory Layout

```
rag-pipeline/
├── README.md
├── requirements.txt
├── .env.example
├── .env
├── app.py
├── artifacts/
│   ├── project_details.md
│   ├── technical_details.md
│   ├── implmentation_plan.md
│   ├── api_reference.md
│   ├── account_setup.md
│   ├── prompts.md
│   └── latency_results.md
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── pipeline.py
│   ├── stt/
│   │   ├── __init__.py
│   │   ├── sarvam_client.py
│   │   ├── elevenlabs_client.py
│   │   └── base.py
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── edge_tts_client.py
│   │   ├── sarvam_tts_client.py
│   │   ├── elevenlabs_client.py
│   │   └── base.py
│   ├── embeddings/
│   │   ├── __init__.py
│   │   ├── voyage_client.py
│   │   ├── gemini_client.py
│   │   └── base.py
│   ├── retrieval/
│   │   ├── __init__.py
│   │   ├── qdrant_client.py
│   │   ├── pinecone_client.py
│   │   ├── retriever.py
│   │   ├── reranker.py
│   │   └── base.py
│   ├── chunking/
│   │   ├── __init__.py
│   │   ├── passage_chunker.py
│   │   ├── fixed_window.py
│   │   ├── sliding_window.py
│   │   ├── semantic_chunker.py
│   │   ├── hierarchical.py
│   │   └── base.py
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── provider_cascade.py
│   │   ├── harness.py
│   │   ├── prompts.py
│   │   └── schemas.py
│   ├── guardrails/
│   │   ├── __init__.py
│   │   ├── input_guard.py
│   │   ├── retrieval_guard.py
│   │   ├── output_guard.py
│   │   └── schemas.py
│   └── analytics/
│       ├── __init__.py
│       ├── timer.py
│       ├── reporter.py
│       └── dashboard.py
├── scripts/
│   ├── prepare_dataset.py
│   ├── run_experiments.py
│   ├── embed_passages.py
│   ├── upload_vectors.py
│   ├── benchmark.py
│   └── test_providers.py
├── data/
│   ├── passages_clean.jsonl
│   ├── embeddings/
│   ├── experiments/
│   └── benchmarks/
└── tests/
    ├── test_stt.py
    ├── test_retrieval.py
    ├── test_generation.py
    ├── test_guardrails.py
    └── test_pipeline.py
```
