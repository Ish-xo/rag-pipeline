# ULTRON-V — Account Setup Checklist

> Every service used is **free tier**. No credit card required.
> Last verified: August 15, 2026.

---

## Required Accounts (Must Have)

### 1. Sarvam AI — STT (Primary) + TTS
- **Signup**: https://dashboard.sarvam.ai
- **What you get**: ₹100 free credits (~200 min STT, ~33K chars TTS)
- **Key name**: `SARVAM_API_KEY`
- **Header**: `api-subscription-key`
- [ ] Account created
- [ ] API key generated
- [ ] Tested STT endpoint
- [ ] Tested TTS endpoint

### 2. ElevenLabs — STT (Backup) + TTS
- **Signup**: https://elevenlabs.io
- **What you get**: 10,000 credits/month (shared across STT + TTS)
- **STT Model**: `scribe_v2` (90+ languages incl. Hindi)
- **Key name**: `ELEVENLABS_API_KEY`
- **Header**: `xi-api-key`
- [ ] Account created
- [ ] API key generated
- [ ] Tested STT Scribe endpoint
- [ ] Tested TTS endpoint

### 3. Groq — Primary LLM (CORE)
- **Signup**: https://console.groq.com
- **What you get**: Free tier (30 RPM, 1000+ RPD)
- **Model**: `llama-3.3-70b-versatile`
- **Key name**: `GROQ_API_KEY`
- [ ] Account created
- [ ] API key generated
- [ ] Tested chat completion

### 4. Cerebras — Backup LLM 1 (CORE)
- **Signup**: https://cloud.cerebras.ai
- **What you get**: 1M tokens/day free, 30 RPM
- **Model**: `llama-3.3-70b`
- **Key name**: `CEREBRAS_API_KEY`
- [ ] Account created
- [ ] API key generated

### 5. Google AI Studio — Backup LLM 2 (CORE) + Backup Embeddings
- **Signup**: https://aistudio.google.com (uses Google account)
- **What you get**: 15 RPM Gemini 2.5 Flash + 1500 RPM embeddings
- **Models**: `gemini-2.5-flash` (LLM), `gemini-embedding-001` (embeddings)
- **Key name**: `GOOGLE_API_KEY`
- [ ] Account created
- [ ] API key generated

---

## Stretch Accounts (Add if time permits)

### 6. SambaNova — Stretch LLM
- **Signup**: https://cloud.sambanova.ai
- **What you get**: 240 RPM, 48K RPD
- **Model**: `Meta-Llama-3.3-70B-Instruct`
- **Key name**: `SAMBANOVA_API_KEY`
- [ ] Account created
- [ ] API key generated

### 7. Together AI — Stretch LLM
- **Signup**: https://api.together.ai
- **What you get**: $5 free credit
- **Model**: `meta-llama/Llama-3.3-70B-Instruct-Turbo`
- **Key name**: `TOGETHER_API_KEY`
- [ ] Account created
- [ ] API key generated

### 8. OpenRouter — Stretch LLM (Last Resort)
- **Signup**: https://openrouter.ai
- **What you get**: 20 RPM, 50 RPD on free models
- **Model**: `google/gemini-2.5-flash:free`
- **Key name**: `OPENROUTER_API_KEY`
- [ ] Account created
- [ ] API key generated

### 9. Voyage AI — Primary Embeddings
- **Signup**: https://dash.voyageai.com
- **What you get**: 200M free tokens
- **Model**: `voyage-3`
- **Key name**: `VOYAGE_API_KEY`
- [ ] Account created
- [ ] API key generated

### 10. Qdrant Cloud — Primary Vector DB
- **Signup**: https://cloud.qdrant.io
- **What you get**: 4 GB disk, 1 GB RAM cluster
- **Key names**: `QDRANT_URL` + `QDRANT_API_KEY`
- [ ] Account created
- [ ] Free cluster created
- [ ] API key generated
- [ ] Cluster URL noted

### 11. Pinecone — Backup Vector DB
- **Signup**: https://app.pinecone.io
- **What you get**: 2 GB storage, serverless
- **Key names**: `PINECONE_API_KEY` + `PINECONE_INDEX_HOST`
- [ ] Account created
- [ ] Serverless index created (1024d, cosine)
- [ ] API key generated
- [ ] Index host URL noted

### 12. Hugging Face — Deployment + Dataset
- **Signup**: https://huggingface.co
- **What you get**: Free Spaces (Gradio), dataset access
- **Key name**: `HF_TOKEN` (for dataset download)
- [ ] Account created
- [ ] Access token generated
- [ ] Space created: `ultron-v`

---

## Optional Accounts

### 13. Jina AI — Backup Embeddings
- **Signup**: https://jina.ai
- **What you get**: 10M free tokens
- **Model**: `jina-embeddings-v4`
- **Key name**: `JINA_API_KEY`
- [ ] Account created (optional)

---

## .env File Template

```env
# === STT ===
SARVAM_API_KEY=
ELEVENLABS_API_KEY=

# === LLM Providers (Core 3 + Stretch 3) ===
GROQ_API_KEY=
CEREBRAS_API_KEY=
GOOGLE_API_KEY=
SAMBANOVA_API_KEY=
TOGETHER_API_KEY=
OPENROUTER_API_KEY=

# === Embeddings ===
VOYAGE_API_KEY=
JINA_API_KEY=

# === Vector Database ===
QDRANT_URL=
QDRANT_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_HOST=

# === Deployment ===
HF_TOKEN=
```

---

## Task Distribution

| Team Member | Accounts to Create |
|-------------|-------------------|
| Member 1 (Backend) | Groq, Cerebras, SambaNova, Together, OpenRouter |
| Member 2 (Data) | Voyage AI, Qdrant, Pinecone, Jina AI, HuggingFace |
| Member 3 (Frontend) | Sarvam AI, ElevenLabs, Google AI Studio, HuggingFace |

> **Tip**: Create all accounts on Day 1. Some services may take time to provision API keys.
