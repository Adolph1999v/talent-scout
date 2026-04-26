
# Fallback LLM chain — tries models in order from fastest
# to most capable. If one hits rate limits, moves to next.

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Models ordered: fastest/most-limited → slowest/most-available
# Each has different rate limits on Groq's free tier
MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
]


def chat(messages: list[dict], temperature: float = 0.1) -> str:
    """
    Drop-in replacement for groq chat completions.
    Tries each model in order — if one hits rate limit (429)
    or any error, automatically falls back to the next.

    Usage:
        from llm_client import chat
        response = chat([{"role": "user", "content": "Hello"}])
    """
    last_error = None

    for model in MODELS:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
            )
            # If we're not using the primary model, log it
            if model != MODELS[0]:
                print(f"⚠️  Using fallback model: {model}")
            return response.choices[0].message.content.strip()

        except Exception as e:
            error_str = str(e)
            # 429 = rate limit, 503 = model unavailable
            if "429" in error_str or "503" in error_str or "rate" in error_str.lower():
                print(f"⚠️  {model} rate limited — trying next model...")
                last_error = e
                continue
            else:
                # Different error (bad prompt, network, etc) — raise immediately
                raise e

    # All models exhausted
    raise Exception(
        f"All models rate limited. Last error: {last_error}\n"
        f"Wait a minute and try again, or add your GROQ_API_KEY to .env"
    )
