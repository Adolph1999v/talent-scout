import os
import json
from dotenv import load_dotenv
from llm_client import chat

load_dotenv()


def simulate_conversation(candidate: dict, parsed_jd: dict) -> list[dict]:
    recruiter_questions = [
        f"Hi {candidate['name'].split()[0]}! We came across your profile and think you could be a great fit for a {parsed_jd['role_title']} role. Are you currently open to new opportunities?",
        f"The role requires {', '.join(parsed_jd['required_skills'][:3])}. How would you rate your experience with these?",
        f"This is a {parsed_jd['seniority']}-level position. What are you looking for in your next move, and what's your current notice period?"
    ]

    system_prompt = f"""You are roleplaying as {candidate['name']}, a {candidate['title']} being contacted by a recruiter.

Your profile:
- Experience: {candidate['experience_years']} years
- Skills: {', '.join(candidate['skills'])}
- Currently open to work: {candidate['open_to_work']}
- Preferred roles: {', '.join(candidate['preferred_roles'])}
- Notice period: {candidate['notice_period_days']} days
- Background: {candidate['summary']}

Instructions:
- Reply naturally as this person would in a professional message
- If open_to_work is false, be politely non-committal
- If open_to_work is true, show genuine interest proportional to how well the role fits
- Keep each reply to 2-4 sentences
- Do NOT break character or mention you are an AI"""

    conversation = []
    messages = [{"role": "system", "content": system_prompt}]

    for question in recruiter_questions:
        conversation.append({"role": "recruiter", "message": question})
        messages.append({"role": "user", "content": question})

        # Use fallback chain for each turn
        reply = chat(messages, temperature=0.7)

        conversation.append({"role": "candidate", "message": reply})
        messages.append({"role": "assistant", "content": reply})

    return conversation


def score_interest(candidate: dict, conversation: list[dict]) -> dict:
    convo_text = ""
    for msg in conversation:
        label = "Recruiter" if msg["role"] == "recruiter" else "Candidate"
        convo_text += f"{label}: {msg['message']}\n\n"

    prompt = f"""You are an expert recruiter evaluating candidate interest from a conversation.

Candidate: {candidate['name']} ({candidate['title']}, {candidate['experience_years']} years exp)
Open to work flag: {candidate['open_to_work']}
Notice period: {candidate['notice_period_days']} days

Conversation:
{convo_text}

Evaluate the candidate's genuine interest and return ONLY a valid JSON object:
{{
    "interest_score": <integer 0-100>,
    "interest_level": "high | medium | low",
    "positive_signals": ["list of things that showed interest"],
    "negative_signals": ["list of things that showed hesitation"],
    "interest_summary": "one sentence summary of the candidate's interest level"
}}

Scoring guide:
- 80-100: Enthusiastic, asks questions, available soon
- 50-79: Interested but cautious, some reservations
- 20-49: Lukewarm, not actively looking
- 0-19: Not interested or explicitly declined

Return ONLY JSON, no markdown."""

    raw = chat([{"role": "user", "content": prompt}], temperature=0.1)
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def run_outreach(candidates: list[dict], parsed_jd: dict) -> list[dict]:
    results = []
    for c in candidates:
        print(f"  Simulating conversation with {c['name']}...")
        conversation = simulate_conversation(c, parsed_jd)
        interest = score_interest(c, conversation)
        results.append({
            **c,
            "conversation": conversation,
            "interest_score": interest["interest_score"],
            "interest_level": interest["interest_level"],
            "positive_signals": interest["positive_signals"],
            "negative_signals": interest["negative_signals"],
            "interest_summary": interest["interest_summary"],
        })
    return results
