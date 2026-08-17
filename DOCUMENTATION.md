# ULTRON-V Voice RAG Pipeline Documentation

This document serves as the comprehensive guide to the architecture, model selection, local execution, and testing procedures for the **ULTRON-V Voice RAG** project.

---

## 🏗️ How We Built This

The project is an ultra-low latency, voice-enabled Retrieval-Augmented Generation (RAG) system built with a modular architecture split into three core workstreams:

1. **Backend & LLM Core (Workstream 1):** We built a resilient "Sequential Cascade" system that gracefully handles API limits and downtime, wrapped in a circuit breaker harness. We also implemented a sub-5ms input/retrieval guardrail system and a Two-Tier output hallucination check.
2. **Data & Retrieval (Workstream 2):** Utilizing Qdrant Cloud for vector storage with HNSW indexing, chunking MSMARCO-XI datasets, and performing dense embeddings.
3. **Frontend & Voice I/O (Workstream 3):** An asynchronous Gradio application configured with a custom "Infinity Ultron" themed UI. It integrates real-time Speech-to-Text (STT) and Text-to-Speech (TTS).

---

## 🧠 Models Used & Their Benefits

### 1. LLM Generation: The Sequential Cascade
* **Groq (`llama-3.3-70b-versatile`)**: Primary provider. 
  * *Benefit*: Insanely fast inference via LPU architecture, consistently delivering Time-To-First-Token (TTFT) under 300ms, essential for real-time voice conversations.
* **Cerebras (`llama-3.3-70b`)**: Secondary fallback provider.
  * *Benefit*: Fast Wafer-Scale Engine processing to take over seamlessly if Groq hits rate limits.
* **Google Gemini (`gemini-2.5-flash`)**: Tertiary fallback & Tier-2 Guardrail Verifier.
  * *Benefit*: Extremely reliable and capable of complex logic checks (like our hallucination verifier).

### 2. Embeddings
* **Voyage AI (`voyage-3`)**: 
  * *Benefit*: State-of-the-art text embedding models optimized for retrieval quality (Recall/NDCG), significantly outperforming standard open-source sentence transformers on complex queries.

### 3. Voice (STT & TTS)
* **Sarvam AI (`saaras:v3` / `bulbul:v3`)** & **ElevenLabs (`scribe_v2`)**:
  * *Benefit*: Sarvam provides unparalleled accuracy for Indian regional languages (Hindi/English mix), while ElevenLabs provides broadcast-quality English synthesis. Both support asynchronous streaming for low latency.

---

## 🔒 Guardrails Architecture

We implemented strict latency budgets to ensure safety without compromising speed:
1. **Input Guardrail (<5ms):** Rejects empty audio and blocks prompt injections using Regex rules.
2. **Retrieval Guardrail (<10ms):** Drops irrelevant documents (Cosine similarity < 0.40) and removes duplicate contexts.
3. **Output Guardrail:**
   * *Tier 1 (Deterministic, <50ms):* Calculates keyword/entity overlap between the LLM output and source documents.
   * *Tier 2 (LLM Verifier, ~200ms):* Only triggered if Tier 1 fails; asks Gemini to logically verify if the answer is hallucinated.

---

## 💻 Local URLs & Execution Scripts

To run the project locally, ensure your `.env` file is populated with your API keys (`GROQ_API_KEY`, `CEREBRAS_API_KEY`, `GOOGLE_API_KEY`, `VOYAGE_API_KEY`, etc.).

### 1. Launch the UI (Gradio)
To start the main Voice RAG interface:
```bash
python app.py
```
* **Local URL:** `http://127.0.0.1:7860`
* *Note: The UI includes a live waterfall diagnostic panel to monitor millisecond latencies for every step of the pipeline.*

### 2. Run Latency Benchmarks
To verify that the retrieval system is adhering to the strict **50ms latency budget**:
```bash
python scripts/benchmark.py 50
```
* *This will run 50 queries through the embedding and search modules, outputting average, p50, and p95 latencies.*

### 3. Run the Test Suite
To run the automated tests validating the circuit breaker harness, sequential cascade, and guardrails:
```bash
python -m pytest tests/test_workstream1.py -v
```

---

## ⏱️ Latency Budget Targets (The "Time Stone Sync")
Our hard performance targets are continuously measured and displayed in the UI:
* **T0 -> T1 (STT):** `< 400ms`
* **T1 -> T2 (Input Guard):** `< 5ms`
* **T2 -> T3 (Embed):** `< 20ms`
* **T3 -> T4 (Search):** `< 30ms`
* **T4 -> T5 (Rerank/Guard):** `< 10ms`
* **T5 -> T6 (LLM TTFT):** `< 300ms`
* **T6 -> T7 (LLM Gen):** `< 1500ms`
* **T7 -> T8 (Output Guard):** `< 50ms`
* **T8 -> T9 (TTS):** `< 400ms`
