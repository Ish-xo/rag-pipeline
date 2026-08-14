# Voice-Enabled RAG Pipeline - HH Goa 2026 Task 2

This repository contains the baseline implementation of a Voice-Enabled RAG (Retrieval-Augmented Generation) system.

## Pipeline Architecture
1. **Voice Input:** Receives audio query.
2. **Speech-to-Text (STT):** Transcribes audio using either Sarvam or ElevenLabs.
3. **Retrieval & Chunking:** 
   - Advanced chunking strategies (semantic, metadata-aware, overlapping windows) applied to the `ai4bharat/MSMARCO-XI` dataset.
   - Vector database retrieval for low-latency context matching.
4. **Answer Generation:** LLM generates an answer strictly grounded in the retrieved context.
5. **Guardrails & Harness:** Checks for off-topic inputs, evaluates context relevance, validates output groundedness, and manages error recovery and retries.

## Project Structure
```text
.
├── src/
│   ├── main.py            # FastAPI entry point
│   ├── pipeline.py        # Core RAG orchestration logic
│   ├── stt.py             # Speech-to-Text integrations
│   ├── retrieval.py       # Vector DB interaction
│   ├── chunking.py        # Dataset indexing and chunking strategies
│   ├── guardrails.py      # Input/Output validation & Hallucination checks
│   └── metrics.py         # Script for P50/P70/P100 latency analytics
├── data/                  # Placeholder for local dataset downloads
├── .env.example           # Example environment variables
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## Getting Started

### Prerequisites
- Python 3.10+
- An STT Provider API Key (Sarvam or ElevenLabs)
- An LLM API Key (e.g., OpenAI, Anthropic, or local open-source LLM)
- (Optional) Docker for running Vector DB locally

### Installation
1. Clone this repository (or initialize git in this directory).
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy the environment file and configure your API keys:
   ```bash
   cp .env.example .env
   ```

### Running the Application
To start the API server:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Analytics & Latency
To hit the strict <200ms latency target, the system heavily relies on fast STT, an optimized vector index, and edge/fast-inference LLMs. 
Run the analytics script to generate P50, P70, and P100 metrics:
```bash
python src/metrics.py
```
