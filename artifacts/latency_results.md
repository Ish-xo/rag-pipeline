# ULTRON-V — Latency Results Template

> This document will be populated after running benchmarks (Phase 4 — Aug 21).

---

## Benchmark Configuration

| Parameter | Value |
|-----------|-------|
| **Test Queries** | 100 queries from MSMARCO-XI Hindi validation set |
| **LLM Provider** | Groq (`llama-3.3-70b-versatile`) — primary |
| **Embedding Provider** | Voyage AI (`voyage-multilingual-2`) |
| **Vector DB** | Qdrant Cloud (free tier) |
| **Top-K Retrieval** | 5 |
| **Retrieval Strategy** | Direct + HyDE (RRF fusion) |
| **Deployment** | Hugging Face Spaces (free CPU) |

---

## Pipeline Stage Latencies

### Retrieval Pipeline (Target: <200ms)

| Metric | P50 | P70 | P100 | Target |
|--------|-----|-----|------|--------|
| Query Embedding | — ms | — ms | — ms | <50ms |
| Vector Search | — ms | — ms | — ms | <30ms |
| **Total Retrieval** | **— ms** | **— ms** | **— ms** | **<200ms** |

### Full Pipeline (End-to-End)

| Metric | P50 | P70 | P100 |
|--------|-----|-----|------|
| STT (Sarvam) | — ms | — ms | — ms |
| Query Processing | — ms | — ms | — ms |
| Retrieval (embed + search) | — ms | — ms | — ms |
| LLM Generation (TTFT) | — ms | — ms | — ms |
| LLM Generation (Total) | — ms | — ms | — ms |
| TTS (edge-tts) | — ms | — ms | — ms |
| **End-to-End** | **— ms** | **— ms** | **— ms** |

---

## Per-Provider LLM Latency Comparison

| Provider | Model | TTFT P50 | TTFT P70 | TTFT P100 | Total P50 |
|----------|-------|----------|----------|-----------|-----------|
| Groq | llama-3.3-70b | — | — | — | — |
| Cerebras | llama-3.3-70b | — | — | — | — |
| SambaNova | Llama-3.3-70B | — | — | — | — |
| Gemini | gemini-2.0-flash | — | — | — | — |
| Together | Llama-3.3-70B-Free | — | — | — | — |

---

## Chunking Strategy Retrieval Quality

| Strategy | Avg Recall@5 | Avg NDCG@5 | Avg Retrieval Latency |
|----------|-------------|-----------|----------------------|
| Passage-level (base) | — | — | — ms |
| Sliding window | — | — | — ms |
| Semantic chunks | — | — | — ms |
| HyDE-enhanced | — | — | — ms |
| RRF ensemble | — | — | — ms |

---

## Raw Data

> Full benchmark CSV will be saved to `data/benchmarks/latency_results.csv`

---

## Notes

- *To be filled after running `scripts/benchmark.py`*
- *P50 = median, P70 = 70th percentile, P100 = maximum (worst case)*
- *TTFT = Time to First Token*
