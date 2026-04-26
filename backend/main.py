import os
import json
import tempfile
import numpy as np
import traceback

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import PyPDF2

from matcher import match_candidates
from outreach import run_outreach
from embeddings import candidates, index, model, profile_to_text
from llm_client import chat

load_dotenv()

app = FastAPI(
    title="AI Talent Scout API",
    description="RAG-powered candidate matching and engagement agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class JDRequest(BaseModel):
    jd_text: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "ok", "message": "Talent Scout API is running", "candidates_indexed": len(candidates)}


@app.get("/candidates")
def get_candidates():
    return {"candidates": candidates, "total": len(candidates)}


@app.post("/analyze")
def analyze(request: JDRequest):
    if not request.jd_text.strip():
        raise HTTPException(status_code=400, detail="JD text cannot be empty")
    try:
        print("\n=== New Analysis Request ===")
        match_result = match_candidates(request.jd_text, top_k=request.top_k)
        parsed_jd = match_result["parsed_jd"]
        matched = match_result["candidates"]

        print("Running outreach simulation...")
        enriched = run_outreach(matched, parsed_jd)

        for c in enriched:
            c["combined_score"] = round(
                0.6 * c["match_score"] + 0.4 * c["interest_score"], 1
            )

        enriched.sort(key=lambda x: x["combined_score"], reverse=True)
        for i, c in enumerate(enriched):
            c["rank"] = i + 1

        return {
            "parsed_jd": parsed_jd,
            "candidates": enriched,
            "total_matched": len(enriched)
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/add-candidate")
async def add_candidate(file: UploadFile = File(...)):
    content = await file.read()

    if file.filename.endswith(".pdf"):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = " ".join(
                    page.extract_text() for page in reader.pages
                    if page.extract_text()
                )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not read PDF: {e}")
    elif file.filename.endswith(".txt"):
        text = content.decode("utf-8")
    else:
        raise HTTPException(status_code=400, detail="Only PDF or .txt files supported")

    if not text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from file")

    prompt = f"""Extract candidate information from this CV/resume.
Return ONLY a valid JSON object with these exact fields:
{{
    "name": "Full name",
    "title": "Current or most recent job title",
    "experience_years": <integer, estimate if unclear>,
    "location": "City, Country if found, else Unknown",
    "skills": ["technical", "skills", "extracted", "from", "cv"],
    "summary": "2-3 sentence professional summary based on their experience",
    "education": "Highest degree and institution",
    "open_to_work": true,
    "preferred_roles": ["2-3 role titles that fit this person"],
    "expected_salary": "Unknown",
    "notice_period_days": 30
}}

Rules:
- skills should be specific technologies and tools, not soft skills
- summary should be written in third person
- Return ONLY JSON, no markdown, no explanation

CV Text:
{text[:3000]}"""

    try:
        raw = chat([{"role": "user", "content": prompt}], temperature=0.1)
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        new_candidate = json.loads(raw.strip())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse CV: {e}")

    new_candidate["id"] = f"uploaded_{len(candidates)+1:03d}"

    text_repr = profile_to_text(new_candidate)
    embedding = model.encode([text_repr], normalize_embeddings=True)
    index.add(np.array(embedding, dtype=np.float32))
    candidates.append(new_candidate)

    print(f"✅ New candidate added: {new_candidate['name']} (total: {len(candidates)})")

    return {
        "message": f"{new_candidate['name']} added to candidate pool successfully",
        "candidate": new_candidate,
        "total_candidates": len(candidates)
    }
