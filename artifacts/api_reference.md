# ULTRON-V — API Reference & Provider Details

> All providers are free tier. No credit card required for any service.
> Last verified: August 15, 2026.

---

## 1. Speech-to-Text (STT)

### 1.1 Sarvam AI STT (PRIMARY)

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

### 1.2 ElevenLabs Scribe STT (BACKUP)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.elevenlabs.io/v1/speech-to-text` |
| **Model** | `scribe_v2` |
| **Auth** | `xi-api-key` header |
| **Free Tier** | 10,000 credits/month (shared with TTS) |
| **Max File Size** | 5.0 GB |
| **Min Audio** | 100ms |
| **Languages** | 90+ languages including Hindi + 10 Indic languages |
| **Request Format** | `multipart/form-data` |
| **SDK** | `pip install elevenlabs` |
| **Signup** | https://elevenlabs.io |
| **Concurrency** | 8 concurrent requests (free tier) |

**Request Fields:**
- `file` (binary): Audio/video file
- `model_id` (string, required): `scribe_v2`
- `language_code` (string, optional): ISO-639 code e.g. `hi`, `en`
- `diarize` (bool, optional): Speaker separation
- `tag_audio_events` (bool, optional): Tag laughter, applause, etc.
- `timestamps_granularity` (string, optional): `word` or `character`

**Response:**
```json
{
  "text": "नमस्ते, आप कैसे हैं?",
  "words": [
    {"text": "नमस्ते", "start": 0.12, "end": 0.55, "speaker_id": "speaker_0"}
  ],
  "language_code": "hi"
}
```

---

## 2. LLM Providers

> **Core 3** providers are always integrated. **Stretch** providers are added if time permits.

### CORE PROVIDERS

### 2.1 Groq (PRIMARY)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.groq.com/openai/v1` |
| **Model** | `llama-3.3-70b-versatile` |
| **Alt Models** | `llama-4-scout-17b-16e-instruct`, `qwen-qwq-32b` |
| **Context Window** | 128,000 tokens (max completion: 32,768) |
| **Rate Limit** | 30 RPM, 12K-30K TPM, 1,000-14,400 RPD |
| **Auth** | `Authorization: Bearer <GROQ_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://console.groq.com |
| **Latency** | ~100-200ms TTFT (LPU hardware) |

**LiteLLM Model String:** `groq/llama-3.3-70b-versatile`

### 2.2 Cerebras (BACKUP 1)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.cerebras.ai/v1` |
| **Model** | `llama-3.3-70b` |
| **Alt Models** | `llama-4-scout-17b-16e`, `qwen-3-32b` |
| **Context Window** | 128,000 tokens |
| **Max Completion** | 8,192 tokens |
| **Rate Limit** | 30 RPM, 60K TPM, 1M tokens/day |
| **Auth** | `Authorization: Bearer <CEREBRAS_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://cloud.cerebras.ai |
| **Latency** | ~100-300ms TTFT |

**LiteLLM Model String:** `cerebras/llama-3.3-70b`

### 2.3 Google Gemini (BACKUP 2)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://generativelanguage.googleapis.com/v1beta` |
| **Model** | `gemini-2.5-flash` |
| **Alt Models** | `gemini-2.5-pro` (2 RPM, 50 RPD) |
| **Context Window** | 1,048,576 tokens (~1M) |
| **Rate Limit** | 15 RPM, 1M TPM, 1,500 RPD |
| **Auth** | `x-goog-api-key` header or `key` query param |
| **SDK** | `pip install google-genai` |
| **Signup** | https://aistudio.google.com |

**LiteLLM Model String:** `gemini/gemini-2.5-flash`

---

### STRETCH PROVIDERS (add if time permits)

### 2.4 SambaNova (STRETCH)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.sambanova.ai/v1` |
| **Model** | `Meta-Llama-3.3-70B-Instruct` |
| **Alt Models** | `DeepSeek-R1`, `QwQ-32B` |
| **Context Window** | 128,000 tokens |
| **Rate Limit** | 240 RPM, 48,000 RPD |
| **Auth** | `Authorization: Bearer <SAMBANOVA_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://cloud.sambanova.ai |

**LiteLLM Model String:** `sambanova/Meta-Llama-3.3-70B-Instruct`

### 2.5 Together AI (STRETCH)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://api.together.ai/v1` |
| **Model** | `meta-llama/Llama-3.3-70B-Instruct-Turbo` |
| **Alt Models** | `deepseek-ai/DeepSeek-R1-Distill-Llama-70B-Free` |
| **Context Window** | 128,000 tokens |
| **Rate Limit** | ~60 RPM (dynamic) |
| **Auth** | `Authorization: Bearer <TOGETHER_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Free Credit** | $5 on signup |
| **Signup** | https://api.together.ai |

**LiteLLM Model String:** `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo`

### 2.6 OpenRouter (STRETCH — Last Resort)

| Detail | Value |
|--------|-------|
| **Base URL** | `https://openrouter.ai/api/v1` |
| **Model** | `google/gemini-2.5-flash:free` |
| **Alt Models** | `meta-llama/llama-3.3-70b-instruct:free`, `qwen/qwen-3-32b:free` |
| **Rate Limit** | 20 RPM, 50 RPD (unfunded) |
| **Auth** | `Authorization: Bearer <OPENROUTER_API_KEY>` |
| **API Format** | OpenAI-compatible |
| **Signup** | https://openrouter.ai |

**LiteLLM Model String:** `openrouter/google/gemini-2.5-flash:free`

---

## 3. Embedding Providers

### 3.1 Voyage AI (PRIMARY)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.voyageai.com/v1/embeddings` |
| **Model** | `voyage-3` |
| **Dimensions** | 1024 |
| **Context** | 32,000 tokens |
| **Free Quota** | 200M tokens on signup |
| **Rate Limit** | 2,000 RPM, 3M-16M TPM |
| **Auth** | `Authorization: Bearer <VOYAGE_API_KEY>` |
| **SDK** | `pip install voyageai` |
| **Signup** | https://dash.voyageai.com |
| **Batch Size** | Up to 128 texts per request |

**Usage:**
```python
import voyageai
vo = voyageai.Client(api_key="...")
result = vo.embed(texts=["query text"], model="voyage-3", input_type="query")
# result.embeddings → [[0.123, -0.456, ...]]
```

### 3.2 Google Gemini Embedding (BACKUP 1)

| Detail | Value |
|--------|-------|
| **Model** | `gemini-embedding-001` |
| **Dimensions** | 768 |
| **Free Quota** | Unlimited (free tier) |
| **Rate Limit** | 1,500 RPM |
| **Context** | 2,048 tokens |
| **SDK** | `pip install google-genai` |

> ⚠️ **Critical Architecture Constraint**: `gemini-embedding-001` generates 768-dimensional vectors. It MUST query a separate `ultron_passages_gemini_768` collection and CANNOT query the primary 1024d Voyage collection. Never pad, truncate, or resize vectors across dimensions.

### 3.3 Jina AI Embedding (BACKUP 2 — STRETCH)

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://api.jina.ai/v1/embeddings` |
| **Model** | `jina-embeddings-v4` |
| **Dimensions** | 1024 (native match with primary collection) |
| **Context** | 32,000 tokens |
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
| **Primary Collection** | `ultron_passages_voyage_1024` (1024d, Cosine) |
| **Fallback Collection** | `ultron_passages_gemini_768` (768d, Cosine) — optional |
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
| **Indexes** | Up to 5 indexes, 100 namespaces/index |
| **Region** | AWS us-east-1 only |
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
| **Free Tier** | 10,000 credits/month (shared with STT) |
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
| **Full Dataset Size** | ~55 GB (all languages) |
| **Hindi Subset Size** | ~4 GB |
| **Fields** | `query`, `Answer`, `query_id`, `query_type`, `passages` |
| **Passage Fields** | `is_selected`, `English_passages`, `Translated_passages` |
| **Query Types** | DESCRIPTION, NUMERIC, ENTITY, LOCATION, PERSON |

**Loading (streaming to avoid full download):**
```python
from datasets import load_dataset

# Stream without downloading full dataset
dataset = load_dataset("ai4bharat/MSMARCO-XI", "hi", split="train", streaming=True)

# Take a subset
subset = dataset.take(50000)
```

**Loading (download Hindi only — ~4 GB, one-time):**
```python
from datasets import load_dataset
dataset = load_dataset("ai4bharat/MSMARCO-XI", "hi", split="train")
```
