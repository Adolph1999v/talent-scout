import os
import json
from dotenv import load_dotenv
from llm_client import chat

load_dotenv()


def parse_jd(jd_text: str) -> dict:
    prompt = f"""You are an expert technical recruiter. Analyze the job description below and extract structured information.

Return ONLY a valid JSON object with these exact fields:
{{
    "role_title": "string — the job title",
    "required_skills": ["list", "of", "must-have", "technical", "skills"],
    "nice_to_have_skills": ["list", "of", "optional", "skills"],
    "experience_years_min": <integer — minimum years required, 0 if not specified>,
    "seniority": "one of: junior | mid | senior | lead | any",
    "key_responsibilities": ["up to 3 short bullet points"],
    "summary": "one sentence describing what this role is about"
}}

Rules:
- required_skills should be specific technologies, not soft skills
- If experience not mentioned, set experience_years_min to 0
- Return ONLY the JSON object, no markdown, no explanation

Job Description:
{jd_text}"""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.1)

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def jd_to_search_text(parsed_jd: dict) -> str:
    skills = ", ".join(parsed_jd.get("required_skills", []))
    nice   = ", ".join(parsed_jd.get("nice_to_have_skills", []))
    resps  = " ".join(parsed_jd.get("key_responsibilities", []))
    return (
        f"{parsed_jd['role_title']} role. "
        f"Seniority: {parsed_jd['seniority']}. "
        f"Required skills: {skills}. "
        f"Nice to have: {nice}. "
        f"Responsibilities: {resps}. "
        f"{parsed_jd['summary']}"
    )
