import os
import json
from dotenv import load_dotenv
from llm_client import chat
from embeddings import search_candidates, index, candidates
from jd_parser import parse_jd, jd_to_search_text

load_dotenv()


def explain_match(candidate: dict, parsed_jd: dict) -> dict:
    prompt = f"""You are a technical recruiter evaluating a candidate for a job.

JOB:
- Role: {parsed_jd['role_title']}
- Required skills: {', '.join(parsed_jd['required_skills'])}
- Nice to have: {', '.join(parsed_jd.get('nice_to_have_skills', []))}
- Min experience: {parsed_jd['experience_years_min']} years
- Seniority: {parsed_jd['seniority']}

CANDIDATE:
- Name: {candidate['name']}
- Title: {candidate['title']}
- Experience: {candidate['experience_years']} years
- Skills: {', '.join(candidate['skills'])}
- Summary: {candidate['summary']}

IMPORTANT MATCHING RULES:
- Match skills SEMANTICALLY, not just exact string match
- "ML" = "Machine Learning", "NLP" = "Natural Language Processing"
- "TensorFlow" and "Keras" match if candidate mentions deep learning, neural networks, CNN, RNN, LSTM
- "Pandas" matches if candidate mentions data manipulation or Python data libraries
- If a candidate's summary or title strongly implies a skill, count it as matched
- Be generous but honest: if there's reasonable evidence, mark it matched

Return ONLY a valid JSON object:
{{
    "matched_skills": ["skills the candidate HAS based on semantic matching"],
    "missing_skills": ["skills with NO evidence in profile or summary"],
    "experience_fit": "strong | partial | weak",
    "explanation": "one sentence: why this candidate is or isn't a good fit"
}}

Return ONLY JSON, no markdown."""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.1)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def match_candidates(jd_text: str, top_k: int = 5) -> dict:
    print("Parsing JD...")
    parsed_jd = parse_jd(jd_text)

    print("Searching candidates via RAG...")
    search_text = jd_to_search_text(parsed_jd)
    matched = search_candidates(search_text, index, candidates, top_k=top_k)

    print(f"Explaining matches for {len(matched)} candidates...")
    enriched = []
    for c in matched:
        explanation = explain_match(c, parsed_jd)
        base_score = c["match_score"]
        if explanation["experience_fit"] == "strong":
            adjusted = min(base_score * 1.1, 100)
        elif explanation["experience_fit"] == "weak":
            adjusted = base_score * 0.85
        else:
            adjusted = base_score

        enriched.append({
            **c,
            "match_score": round(adjusted, 1),
            "matched_skills": explanation["matched_skills"],
            "missing_skills": explanation["missing_skills"],
            "experience_fit": explanation["experience_fit"],
            "match_explanation": explanation["explanation"],
            "interest_score": 0,
            "conversation": [],
        })

    return {"parsed_jd": parsed_jd, "candidates": enriched}
