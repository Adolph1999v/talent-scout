
# Loads candidate profiles, converts them into embeddings, stores them in FAISS, and finds best matches for a job description.
import json
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

# Load a lightweight embedding model that converts text into 384-number vectors.
# Downloads once on first use, then saves locally for reuse.

model = SentenceTransformer("all-MiniLM-L6-v2")

# Load candidate profiles

def load_candidates(path: str = "candidates.json") -> list[dict]:
    with open(path, "r") as f:
        return json.load(f)

# Convert each candidate profile into one text string.
# This lets the model read profile details and turn them into a vector.

def profile_to_text(candidate: dict) -> str:
    skills = ", ".join(candidate["skills"])
    roles  = ", ".join(candidate["preferred_roles"])
    return (
        f"{candidate['name']} is a {candidate['title']} "
        f"with {candidate['experience_years']} years of experience. "
        f"Skills: {skills}. "
        f"{candidate['summary']} "
        f"Preferred roles: {roles}. "
        f"Education: {candidate['education']}."
    )

# Build a FAISS index to store candidate vectors and search quickly.
# It compares vectors using similarity scores to find best candidate matches.

def build_index(candidates: list[dict]):
    # Convert each candidate profile to a text string
    texts = [profile_to_text(c) for c in candidates]

    # Embed all texts → shape: (15, 384)
    embeddings = model.encode(texts, normalize_embeddings=True)


    # Create FAISS index that holds 384-dimensional vectors
    dimension = embeddings.shape[1]  # = 384
    index = faiss.IndexFlatIP(dimension)

    # Add all candidate vectors to the index
    # FAISS stores them internally, numbered 0 to 14
    index.add(np.array(embeddings, dtype=np.float32))

    return index, embeddings

# Search top matching candidates for a job description.
# Converts the JD into a vector and finds the closest profiles using FAISS.

def search_candidates(
    jd_text: str,
    index,
    candidates: list[dict],
    top_k: int = 5
) -> list[dict]:

    # Embed the JD — must use same model so vectors are comparable
    jd_vector = model.encode([jd_text], normalize_embeddings=True)

    # Search the FAISS index
    distances, indices = index.search(
        np.array(jd_vector, dtype=np.float32), top_k
    )

    results = []
    for rank, (idx, score) in enumerate(zip(indices[0], distances[0])):
        candidate = candidates[idx].copy()
       
        candidate["match_score"] = round(float(score) * 100, 1)
        candidate["rank"] = rank + 1

        results.append(candidate)

    return results

# Runs once when the file is imported at startup.
# This avoids rebuilding candidate embeddings on every request.

candidates  = load_candidates()
index, _    = build_index(candidates)

print(f"✅ FAISS index built: {len(candidates)} candidates indexed.")