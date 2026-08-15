# ULTRON-V — Account Setup Checklist

> Every service used is **free tier**. No credit card required.

---

## Required Accounts (Must Have)

### 1. Sarvam AI — STT + TTS
- **Signup**: https://dashboard.sarvam.ai
- **What you get**: ₹100 free credits (~200 min STT, ~33K chars TTS)
- **Key name**: `SARVAM_API_KEY`
- **Header**: `api-subscription-key`
- [ ] Account created
- [ ] API key generated
- [ ] Tested STT endpoint
- [ ] Tested TTS endpoint

### 2. Groq — Primary LLM
- **Signup**: https://console.groq.com
- **What you get**: Free tier (30 RPM, 1000 RPD)
- **Key name**: `GROQ_API_KEY`
- [ ] Account created
- [ ] API key generated
- [ ] Tested chat completion

### 3. Cerebras — Backup LLM 1
- **Signup**: https://cloud.cerebras.ai
- **What you get**: 1M tokens/day free
- **Key name**: `CEREBRAS_API_KEY`
- [ ] Account created
- [ ] API key generated

### 4. SambaNova — Backup LLM 2
- **Signup**: https://cloud.sambanova.ai
- **What you get**: 240 RPM, 48K RPD
- **Key name**: `SAMBANOVA_API_KEY`
- [ ] Account created
- [ ] API key generated

### 5. Google AI Studio — Backup LLM 3 + Backup Embeddings
- **Signup**: https://aistudio.google.com (uses Google account)
- **What you get**: 15 RPM Gemini Flash + 1500 RPM embeddings
- **Key name**: `GOOGLE_API_KEY`
- [ ] Account created
- [ ] API key generated

### 6. Together AI — Backup LLM 4
- **Signup**: https://api.together.ai
- **What you get**: $5 free credit
- **Key name**: `TOGETHER_API_KEY`
- [ ] Account created
- [ ] API key generated

### 7. OpenRouter — Backup LLM 5 (Last Resort)
- **Signup**: https://openrouter.ai
- **What you get**: 20 RPM, 50 RPD on free models
- **Key name**: `OPENROUTER_API_KEY`
- [ ] Account created
- [ ] API key generated

### 8. Voyage AI — Primary Embeddings
- **Signup**: https://dash.voyageai.com
- **What you get**: 50M free tokens
- **Key name**: `VOYAGE_API_KEY`
- [ ] Account created
- [ ] API key generated

### 9. Qdrant Cloud — Primary Vector DB
- **Signup**: https://cloud.qdrant.io
- **What you get**: 4 GB disk, 1 GB RAM cluster
- **Key name**: `QDRANT_URL` + `QDRANT_API_KEY`
- [ ] Account created
- [ ] Free cluster created
- [ ] API key generated
- [ ] Cluster URL noted

### 10. Pinecone — Backup Vector DB
- **Signup**: https://app.pinecone.io
- **What you get**: 2 GB storage, serverless
- **Key name**: `PINECONE_API_KEY` + `PINECONE_INDEX_HOST`
- [ ] Account created
- [ ] Serverless index created (1024d, cosine)
- [ ] API key generated
- [ ] Index host URL noted

### 11. Hugging Face — Deployment + Dataset
- **Signup**: https://huggingface.co
- **What you get**: Free Spaces (Gradio), dataset access
- **Key name**: `HF_TOKEN` (for dataset download)
- [ ] Account created
- [ ] Access token generated
- [ ] Space created: `ultron-v`

---

## Optional Accounts

### 12. Jina AI — Backup Embeddings
- **Signup**: https://jina.ai
- **What you get**: 10M free tokens
- **Key name**: `JINA_API_KEY`
- [ ] Account created (optional)

### 13. ElevenLabs — Premium TTS
- **Signup**: https://elevenlabs.io
- **What you get**: 10,000 chars/month
- **Key name**: `ELEVENLABS_API_KEY`
- [ ] Account created (optional)

---

## .env File Template

```env
# === STT ===
SARVAM_API_KEY=

# === LLM Providers (in cascade order) ===
GROQ_API_KEY=
CEREBRAS_API_KEY=
SAMBANOVA_API_KEY=
GOOGLE_API_KEY=
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

# === TTS ===
ELEVENLABS_API_KEY=

# === Deployment ===
HF_TOKEN=
```

---

## Task Distribution

| Team Member | Accounts to Create |
|-------------|-------------------|
| Member 1 (Backend) | Groq, Cerebras, SambaNova, Together, OpenRouter |
| Member 2 (Data) | Voyage AI, Qdrant, Pinecone, Jina AI, HuggingFace |
| Member 3 (Frontend) | Sarvam AI, Google AI Studio, ElevenLabs, HuggingFace |

> **Tip**: Create all accounts on Day 1. Some services may take time to provision API keys.
