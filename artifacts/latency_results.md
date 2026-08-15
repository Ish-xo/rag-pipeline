# ULTRON-V — Latency & Quality Results

> To be populated after running experiments and benchmarks.

---

## Benchmark Configuration

| Parameter | Value |
|-----------|-------|
| **Development Queries** | 50 queries from deterministic held-out dev split (tuning only) |
| **Test Queries** | 100 queries from deterministic held-out test split (final numbers) |
| **LLM Provider** | Groq (`llama-3.3-70b-versatile`) — primary |
| **Embedding Provider** | Voyage AI (`voyage-3`, 1024d) |
| **Vector DB** | Qdrant Cloud (`ultron_passages_voyage_1024`) |
| **Top-K Retrieval** | 5 |
| **Deployment** | Hugging Face Spaces (free CPU) |

> ⚠️ Development and test query sets are **strictly disjoint with zero ground-truth leakage into the corpus index**. We never tune or optimize on test benchmark queries.

---

## Experiment 1: Incremental Dataset Size

| Subset | Passages | Recall@5 | NDCG@5 | Retrieval P50 | Storage |
|--------|----------|----------|--------|---------------|---------|
| 10K | 10,000 | — | — | — ms | — MB |
| 50K | 50,000 | — | — | — ms | — MB |
| 100K | 100,000 | — | — | — ms | — MB |

**Selected Corpus Size**: ___ (smallest subset satisfying target retrieval quality)

---

## Experiment 2: Indexing Language

| Experiment | Index Language | Query Language | Recall@5 | NDCG@5 |
|------------|---------------|----------------|----------|--------|
| A | English passages | English queries | — | — |
| B | Hindi passages | Hindi queries | — | — |
| C | English passages | Hindi queries (cross-lingual) | — | — |
| D | Dual English + Hindi | Hindi queries | — | — |

**Selected Configuration**: ___

---

## Experiment 3: Chunking Strategy Quality (Isolated Test Collections)

| Strategy | Recall@5 | NDCG@5 | Avg Retrieval Latency |
|----------|----------|--------|-----------------------|
| Native passage-level (Base) | — | — | — ms |
| Fixed token window (128) | — | — | — ms |
| Sliding window (256/64) | — | — | — ms |
| Semantic sentence grouping | — | — | — ms |
| Parent-child hierarchical | — | — | — ms |

**Selected Production Strategy**: ___ (Single strategy indexed for production deployment)

---

## Pipeline Latency — Fast Path (Default)

| Metric | P50 | P70 | P100 | Target |
|--------|-----|-----|------|--------|
| Query Embedding (Voyage-3) | — ms | — ms | — ms | <50ms |
| Vector Search (Qdrant 1024d) | — ms | — ms | — ms | <30ms |
| Reranking + Retrieval Guardrails | — ms | — ms | — ms | <20ms |
| **Total Retrieval Latency** | **— ms** | **— ms** | **— ms** | **<100ms** |
| LLM TTFT (Groq) | — ms | — ms | — ms | <200ms* |
| Full LLM Text Generation | — ms | — ms | — ms | — |
| Output Grounding Check (Tier 1) | — ms | — ms | — ms | <10ms |

*\*Note: TTFT is an optimization metric measuring time to first streaming token. It does not constitute proof of full end-to-end completion under 200ms; all stages are measured and reported separately.*

---

## Pipeline Latency — Quality Path (Opt-in Ensemble)

| Metric | P50 | P70 | P100 |
|--------|-----|-----|------|
| Query Expansion (LLM) | — ms | — ms | — ms |
| HyDE Generation (LLM + Embed) | — ms | — ms | — ms |
| 3× Parallel Vector Search | — ms | — ms | — ms |
| RRF Fusion & Reranking | — ms | — ms | — ms |
| **Total Retrieval Latency** | **— ms** | **— ms** | **— ms** |
| LLM TTFT | — ms | — ms | — ms |
| Full LLM Text Generation | — ms | — ms | — ms |

---

## End-to-End Latency Summary

| Pipeline Scope | Stages Included | Target | P50 | P70 | P100 |
|---|---|---|---|---|---|
| **Retrieval Latency** | Query Embedding + Qdrant Search + Reranker (T5 - T2) | **<100ms** | — ms | — ms | — ms |
| **Post-STT Time to First Output (Official Primary Target)** | Query Text Ready (T1) → Groq TTFT (T6) | **<200ms** | — ms | — ms | — ms |
| **Post-STT Full Validated Output** | Query Text Ready (T1) → Grounded Answer (T8) | — | — ms | — ms | — ms |
| **Full Voice Pipeline (with TTS)** | Audio Received (T0) → Audio Playback Ready (T9) | — | — ms | — ms | — ms |

---

## Detailed Stage Latency Breakdown (Full Voice Pipeline)

| Stage | Component / Provider | P50 | P70 | P100 |
|-------|----------------------|-----|-----|------|
| T0 → T1 | STT (Sarvam `saaras:v3`) | — ms | — ms | — ms |
| T1 → T2 | Input Guardrails (Deterministic) | — ms | — ms | — ms |
| T2 → T5 | Fast Path Retrieval (Voyage + Qdrant) | — ms | — ms | — ms |
| T5 → T6 | LLM TTFT (Groq `llama-3.3-70b-versatile`) | — ms | — ms | — ms |
| T6 → T7 | Full LLM Generation | — ms | — ms | — ms |
| T7 → T8 | Output Grounding Check | — ms | — ms | — ms |
| T8 → T9 | TTS Synthesis (`edge-tts`) | — ms | — ms | — ms |
| **Total** | **Full E2E Pipeline (T0 → T9)** | **— ms** | **— ms** | **— ms** |

---

## Per-Provider LLM Latency Comparison

| Provider | Canonical Model | TTFT P50 | TTFT P70 | TTFT P100 | Total P50 |
|----------|-----------------|----------|----------|-----------|-----------|
| **Groq (Core 1)** | `llama-3.3-70b-versatile` | — | — | — | — |
| **Cerebras (Core 2)** | `llama-3.3-70b` | — | — | — | — |
| **Google Gemini (Core 3)** | `gemini-2.5-flash` | — | — | — | — |

---

## Retrieval Strategy Quality Comparison (Quality Path)

| Strategy | Recall@5 | NDCG@5 | Latency P50 |
|----------|----------|--------|-------------|
| Direct embedding only | — | — | — ms |
| Query expansion | — | — | — ms |
| HyDE | — | — | — ms |
| RRF ensemble (Direct + Exp + HyDE) | — | — | — ms |

---

## Raw Benchmark Storage

- Full benchmark CSV: `data/benchmarks/latency_results.csv`
- Experiment logs: `data/experiments/`

---

## Terminology & Measurement Notes

- **P50**: 50th percentile / median duration across benchmark runs.
- **P70**: 70th percentile duration.
- **P100**: Worst-case execution time across all test queries.
- **TTFT**: Time to First Token delivered by the LLM inference provider.
- **Retrieval Latency**: Time elapsed from query receipt to ranked passage return (zero LLM calls on fast path).
