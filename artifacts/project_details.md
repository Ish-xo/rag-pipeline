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

## 📅 Timeline

| Date | Milestone |
|------|-----------|
| Aug 13 | Task launched |
| Aug 15 | Planning complete, architecture finalized |
| Aug 16-17 | Dataset processing, embedding, vector DB setup |
| Aug 18-19 | RAG pipeline core (retrieval + generation + harness + guardrails) |
| Aug 20 | Frontend UI, STT/TTS integration, deployment to HF Spaces |
| Aug 21 | Latency benchmarking (P50/P70/P100), testing, bug fixes |
| Aug 22 | Videos recorded, social media posts, **submission by 11:59 PM** |

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

Everything runs on **free tiers only**. No paid APIs. No credit card required for any service. Multiple backup providers to avoid rate limiting.
