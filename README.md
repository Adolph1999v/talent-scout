# 🎯 AI Talent Scout

> AI-powered talent scouting and engagement agent

🌐 **Live Demo:** https://talentscout-nine.vercel.app
⚙️ **API:** https://adolphvijay-talent-scout-api.hf.space/health

## What it does
- Takes a **Job Description** as input
- Discovers matching candidates using **RAG** (FAISS + sentence-transformers)
- Simulates recruiter ↔ candidate conversations to assess **genuine interest**
- Outputs a **ranked shortlist** scored on Match Score + Interest Score
- Supports **live CV upload** — upload any resume and it's instantly searchable

## Architecture

<img width="550" height="600" alt="image" src="https://github.com/user-attachments/assets/01518dcd-48fd-4413-91b5-caad15ee3f4b" />


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
