# 🎯 AI Talent Scout

> AI-powered talent scouting and engagement agent — built for the Catalyst Hackathon by Deccan AI.

🌐 **Live Demo:** https://talentscout-nine.vercel.app
⚙️ **API:** https://adolphvijay-talent-scout-api.hf.space/health

## What it does
- Takes a **Job Description** as input
- Discovers matching candidates using **RAG** (FAISS + sentence-transformers)
- Simulates recruiter ↔ candidate conversations to assess **genuine interest**
- Outputs a **ranked shortlist** scored on Match Score + Interest Score
- Supports **live CV upload** — upload any resume and it's instantly searchable

## Architecture

JD Input
→ Groq (Llama 3.3 70B) parses JD into structured requirements
→ sentence-transformers embeds JD into vector
→ FAISS retrieves top-K semantically matching candidates  ← RAG
→ Groq explains WHY each candidate matches (explainability)
→ Groq simulates recruiter ↔ candidate conversation
→ Groq scores genuine interest from conversation
→ Combined score = 60% Match + 40% Interest
→ Ranked shortlist returned to recruiter

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | FastAPI + Uvicorn |
| LLM | Groq — Llama 3.3 70B (free tier) with 4-model fallback chain |
| Vector Search | FAISS (Meta) + sentence-transformers |
| Frontend | React + Vite |
| Deployment | HuggingFace Spaces (backend) + Vercel (frontend) |

## Scoring Logic
- **Match Score** — RAG cosine similarity + Groq semantic skill analysis + experience fit
- **Interest Score** — Groq evaluates simulated conversation for enthusiasm, availability, role alignment  
- **Combined Score** — 60% Match + 40% Interest

## LLM Fallback Chain
Automatically falls back across 4 Groq models if rate limits are hit:
1. `llama-3.3-70b-versatile` (primary)
2. `llama-3.1-8b-instant` (fallback 1)
3. `gemma2-9b-it` (fallback 2)
4. `mixtral-8x7b-32768` (fallback 3)

## Local Setup

### Prerequisites
- Python 3.10+
- Node.js 18+
- Free Groq API key from https://console.groq.com

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "GROQ_API_KEY=your_key_here" > .env
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open **http://localhost:5173**

## CV Upload
Upload any PDF or .txt resume — Groq parses it and indexes it into FAISS live.
The candidate is immediately included in the next JD search.

Uploaded CVs are held in memory for the duration of the server session and cleared on restart. This is intentional for the prototype — in production, we'd use a proper database with user-scoped storage so each recruiter sees only their own uploaded candidates.

## Future Plans
- Persistent storage with PostgreSQL + pgvector
- Real ATS integrations (Greenhouse, Workday)
- Batch CV upload
- Recruiter authentication and saved searches
- Live candidate sourcing via LinkedIn API

## Built by
**Adolph Vijay** · [GitHub](https://github.com/Adolph1999v)
