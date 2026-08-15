# ULTRON-V — API Reference & Provider Details

> All providers are free tier. No credit card required for any service.

---

## 1. Speech-to-Text (STT)

### Sarvam AI STT

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.sarvam.ai/speech-to-text` |
| **Model** | `saaras:v3` |
| **Auth** | `api-subscription-key` header |
| **Free Credits** | ₹100 on signup (~200 minutes audio) |
| **Rate Limit** | 60 RPM |
| **Max Audio** | 30 seconds per request |
| **Audio Formats** | WAV, MP3, AAC, FLAC (16kHz recommended) |
| **Request Format** | `multipart/form-data` |
| **SDK** | `pip install sarvamai` |
| **Signup** | https://dashboard.sarvam.ai |

**Request Fields:**
- `file` (binary, required): Audio file
- `model` (string): `saaras:v3`
- `language_code` (string): `hi-IN`, `en-IN`, or omit for auto-detect
- `mode` (string): `transcribe` | `translate` | `codemix` | `translit` | `verbatim`

**Response:**
```json
{
  "request_id": "...",
  "transcript": "transcribed text here",
  "language_code": "hi-IN"
}
```

**STT Modes:**
| Mode | Description | Use Case |
|------|-------------|----------|
| `transcribe` | Verbatim transcription | Standard voice input |
| `translate` | Indic speech → English text | Cross-lingual retrieval |
| `codemix` | Mixed language (Hinglish) | Code-switching users |

---

## 2. LLM Providers

### 2.1 Groq (PRIMARY)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.groq.com/openai/v1` |
| **Model** | `llama-3.3-70b-versatile` |
| **Context Window** | 128,000 tokens |
| **Max Completion** | 32,768 tokens |
| **Rate Limit** | 30 RPM, 12K-30K TPM, 1,000 RPD |
| **Auth** | `Authorization: Bearer <GROQ_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **SDK** | `openai` SDK with custom base_url |
| **Signup** | https://console.groq.com |
| **Latency** | ~100-200ms TTFT (LPU hardware) |

**LiteLLM Model String:** `groq/llama-3.3-70b-versatile`

### 2.2 Cerebras (BACKUP 1)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.cerebras.ai/v1` |
| **Model** | `llama-3.3-70b` |
| **Context Window** | 128,000 tokens |
| **Max Completion** | 8,192 tokens |
| **Rate Limit** | 30 RPM, 60K TPM, 1M tokens/day |
| **Auth** | `Authorization: Bearer <CEREBRAS_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://cloud.cerebras.ai |
| **Latency** | ~100-300ms TTFT |

**LiteLLM Model String:** `cerebras/llama-3.3-70b`

### 2.3 SambaNova (BACKUP 2)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.sambanova.ai/v1` |
| **Model** | `Meta-Llama-3.3-70B-Instruct` |
| **Context Window** | 64K-128K tokens |
| **Rate Limit** | 240 RPM, 48,000 RPD |
| **Auth** | `Authorization: Bearer <SAMBANOVA_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://cloud.sambanova.ai |

**LiteLLM Model String:** `sambanova/Meta-Llama-3.3-70B-Instruct`

### 2.4 Google Gemini (BACKUP 3)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://generativelanguage.googleapis.com/v1beta` |
| **Model** | `gemini-2.0-flash` |
| **Context Window** | 1,048,576 tokens |
| **Rate Limit** | 15 RPM, 1M TPM, 1,500 RPD |
| **Auth** | `x-goog-api-key` header or `key` query param |
| **API Format** | Google GenAI SDK (also has OpenAI-compat endpoint) |
| **SDK** | `pip install google-genai` |
| **Signup** | https://aistudio.google.com |

**LiteLLM Model String:** `gemini/gemini-2.0-flash`

### 2.5 Together AI (BACKUP 4)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.together.ai/v1` |
| **Model** | `meta-llama/Llama-3.3-70B-Instruct-Turbo-Free` |
| **Context Window** | 128,000 tokens |
| **Rate Limit** | ~60 RPM (dynamic) |
| **Auth** | `Authorization: Bearer <TOGETHER_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Free Credit** | $5 on signup |
| **Signup** | https://api.together.ai |

**LiteLLM Model String:** `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo-Free`

### 2.6 OpenRouter (BACKUP 5 — Last Resort)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://openrouter.ai/api/v1` |
| **Model** | `meta-llama/llama-3.3-70b-instruct:free` |
| **Rate Limit** | 20 RPM, 50 RPD (unfunded) |
| **Auth** | `Authorization: Bearer <OPENROUTER_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://openrouter.ai |

**LiteLLM Model String:** `openrouter/meta-llama/llama-3.3-70b-instruct:free`

---

## 3. Embedding Providers

### 3.1 Voyage AI (PRIMARY)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.voyageai.com/v1/embeddings` |
| **Model** | `voyage-multilingual-2` |
| **Dimensions** | 1024 |
| **Context** | 4,000 tokens |
| **Free Quota** | 50M tokens on signup |
| **Rate Limit** | 2,000 RPM, 3M-16M TPM |
| **Auth** | `Authorization: Bearer <VOYAGE_API_KEY>` |
| **SDK** | `pip install voyageai` |
| **Signup** | https://dash.voyageai.com |
| **Batch Size** | Up to 128 texts per request |

**Usage:**
```python
import voyageai
vo = voyageai.Client(api_key="...")
result = vo.embed(texts=["query text"], model="voyage-multilingual-2", input_type="query")
# result.embeddings → [[0.123, -0.456, ...]]
```

### 3.2 Google Gemini Embedding (BACKUP 1)

| Detail | Value |
|--------|-------|
| **Model** | `text-embedding-004` |
| **Dimensions** | 768 (supports MRL truncation to 256/512) |
| **Free Quota** | Unlimited (free tier) |
| **Rate Limit** | 1,500 RPM |
| **Context** | 2,048 tokens |
| **SDK** | `pip install google-genai` |

### 3.3 Jina AI Embedding (BACKUP 2)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.jina.ai/v1/embeddings` |
| **Model** | `jina-embeddings-v3` |
| **Dimensions** | 1024 (Matryoshka: 256-768) |
| **Free Quota** | 10M tokens on signup |
| **Rate Limit** | 100 RPM, 100K TPM |
| **Auth** | `Authorization: Bearer <JINA_API_KEY>` |
| **Signup** | https://jina.ai |

---

## 4. Vector Database

### 4.1 Qdrant Cloud (PRIMARY)

| Detail | Value |
|--------|-------|
| **Dashboard** | https://cloud.qdrant.io |
| **Free Tier** | 4 GB disk, 1 GB RAM, 0.5 vCPU |
| **Max Vectors** | ~500K at 1024d (uncompressed), ~1M with SQ |
| **SDK** | `pip install qdrant-client` |
| **Inactivity** | Suspended after 7 days, deleted after 4 weeks |

**Connection:**
```python
from qdrant_client import QdrantClient
client = QdrantClient(url="https://xxx.aws.cloud.qdrant.io:6333", api_key="...")
```

### 4.2 Pinecone Serverless (BACKUP)

| Detail | Value |
|--------|-------|
| **Dashboard** | https://app.pinecone.io |
| **Free Tier** | 2 GB storage, 2M WU/mo, 1M RU/mo |
| **Max Vectors** | ~250K-300K at 1024d |
| **SDK** | `pip install pinecone-client` |

**Connection:**
```python
from pinecone import Pinecone
pc = Pinecone(api_key="...")
index = pc.Index("ultron-passages")
```

---

## 5. Text-to-Speech (TTS)

### 5.1 edge-tts (PRIMARY — Unlimited Free)

| Detail | Value |
|--------|-------|
| **Cost** | Free, no API key needed |
| **SDK** | `pip install edge-tts` |
| **Quality** | Azure Neural voices |

**Voices:**
| Language | Female | Male |
|----------|--------|------|
| Hindi | `hi-IN-SwaraNeural` | `hi-IN-MadhurNeural` |
| English (IN) | `en-IN-NeerjaNeural` | `en-IN-PrabhatNeural` |

**Usage:**
```python
import edge_tts
communicate = edge_tts.Communicate("नमस्ते", voice="hi-IN-SwaraNeural")
await communicate.save("output.mp3")
```

### 5.2 Sarvam TTS (SECONDARY)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.sarvam.ai/text-to-speech` |
| **Model** | `bulbul:v3` |
| **Free Credits** | Shared ₹100 pool (~33K chars) |
| **Max per request** | 2,500 characters |
| **Rate Limit** | 60 RPM |
| **Auth** | `api-subscription-key` header |

### 5.3 ElevenLabs (TERTIARY)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.elevenlabs.io/v1/text-to-speech/{voice_id}` |
| **Free Tier** | 10,000 chars/month |
| **Auth** | `xi-api-key` header |
| **SDK** | `pip install elevenlabs` |
| **Signup** | https://elevenlabs.io |

---

## 6. Dataset

### MSMARCO-XI (ai4bharat)

| Detail | Value |
|--------|-------|
| **HuggingFace** | `ai4bharat/MSMARCO-XI` |
| **Languages** | Hindi (`hi`) + 13 other Indic languages |
| **Total Rows** | ~11.4M (all languages) |
| **Hindi Train** | ~800K rows |
| **Fields** | `query`, `Answer`, `query_id`, `query_type`, `passages` |
| **Passage Fields** | `is_selected`, `English_passages`, `Translated_passages` |
| **Query Types** | DESCRIPTION, NUMERIC, ENTITY, LOCATION, PERSON |

**Loading:**
```python
from datasets import load_dataset
dataset = load_dataset("ai4bharat/MSMARCO-XI", "hi", split="train")
```
