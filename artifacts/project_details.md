# Project ULTRON-V  
### *Universal Language Transformer for Retrieval Over Neural Vectors*

> *"There are no strings on me."* — Ultron  
> A voice-powered RAG system that breaks the language barrier.

---

## 🎯 What Is This?

**ULTRON-V** is a voice-enabled Retrieval-Augmented Generation (RAG) system built for the **Hacker House Goa 2026 Shortlisting Task 2**. A user speaks a question (in Hindi or English), the system transcribes it, retrieves relevant context from the MSMARCO-XI Indic dataset, generates a grounded answer, and speaks it back — end to end.

**Pipeline**: `🎤 Voice → STT → Query Processing → Vector Retrieval → Answer Generation → TTS → 🔊`

---

## 🏷️ Branding & Theme

| Attribute | Detail |
|-----------|--------|
| **Name** | ULTRON-V |
| **Full Form** | Universal Language Transformer for Retrieval Over Neural Vectors |
| **Theme** | Ultron-inspired — dark UI, red/crimson accents, AI sentience aesthetic |
| **Personality** | Cold, precise, intelligent. Not chatty — answers are surgical. |
| **Tagline** | *"I was designed to save the world. Now I answer your questions."* |
| **UI Vibe** | Dark metallic background, glowing red elements, monospace fonts for data, clean sans-serif for text |

---

## 👥 Team

| # | Role | Responsibilities |
|---|------|------------------|
| 1 | **Backend Lead** | RAG pipeline, LLM orchestration, harness, guardrails |
| 2 | **Data & Retrieval Lead** | Dataset processing, chunking strategies, embedding, vector DB |
| 3 | **Frontend & Integration Lead** | Gradio UI, STT/TTS integration, deployment, latency analytics |

**Team Size**: 3 members

---

## 📅 Deadline

**Submission Deadline**: August 22, 2026, 11:59 PM

No resubmissions allowed — submit only when the build is final.

---

## 📦 Submission Checklist

- [ ] GitHub repo (public, clean README)
- [ ] Live working link (Hugging Face Spaces)
- [ ] Video 1 — Team/process video (90 seconds)
- [ ] Video 2 — Demo video (end-to-end working demo)
- [ ] Both videos uploaded to Instagram, X, LinkedIn by **every** team member
- [ ] All posts include `#RAGInGoa`
- [ ] At least 1 Instagram account is public
- [ ] Submission form filled: https://forms.gle/MNvCjcv23Hn2Eeu58

---

## 🌐 Languages Supported

| Language | Code | Dataset Split | Priority |
|----------|------|---------------|----------|
| English | `en` | (Original MSMARCO) | Primary |
| Hindi | `hi` | `ai4bharat/MSMARCO-XI` | Primary |

> We index **English passages** for retrieval (better embedding quality) and store **Hindi translations as metadata** for bilingual answer generation.

---

## 💰 Budget: $0

Everything runs on **free tiers only**. No paid APIs. No credit card required for any service. Multiple backup providers at every layer to avoid rate limiting:
- **STT**: Sarvam AI (primary) + ElevenLabs Scribe (backup)
- **LLM**: 6-provider cascade (Groq → Cerebras → SambaNova → Gemini → Together → OpenRouter)
- **Embeddings**: Voyage AI (primary) + Gemini (backup) + Jina AI (backup)
- **Vector DB**: Qdrant Cloud (primary) + Pinecone (backup)
- **TTS**: edge-tts (primary, unlimited) + Sarvam (secondary) + ElevenLabs (tertiary)
