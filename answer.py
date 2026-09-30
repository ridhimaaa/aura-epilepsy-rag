import os
import re
import time

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types
from sentence_transformers import SentenceTransformer

load_dotenv()

# ---- Settings you can tweak -------------------------------------------------
GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash-lite"]  # tries in order # change if Google renames/retires it
TOP_K = 5                          # how many different papers to use
MAX_DISTANCE = 0.75                # above this, a match is treated as irrelevant
# -----------------------------------------------------------------------------

DISCLAIMER = "For research and education only. This is not medical advice."

# Phrases that suggest a personal medical question rather than a research one.
PERSONAL_PATTERNS = [
    r"\bdo i have\b",
    r"\bam i (having|epileptic)\b",
    r"\bi (had|have had|am having|got) a seizure\b",
    r"\bshould i (take|stop|start|change)\b",
    r"\bmy (child|son|daughter|baby|husband|wife|mother|father|friend)\b.*\b(seizure|epilep)",
    r"\bdiagnose me\b",
    r"\bwhat dose should i\b",
]

SYSTEM_PROMPT = (
    "You are an epilepsy research assistant for students and researchers. "
    "Answer ONLY using the numbered sources provided. "
    "Cite every claim with the source number in square brackets, like [1] or [2][3]. "
    "If the sources do not contain the answer, reply exactly: "
    "\"I couldn't find this in the available sources.\" "
    "Never use outside knowledge, never give personal medical advice, "
    "never diagnose, and never recommend doses for an individual."
)

embedder = SentenceTransformer("all-MiniLM-L6-v2")
collection = chromadb.PersistentClient(path="chroma_db").get_collection("epilepsy")
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def is_personal_question(question):
    q = question.lower()
    return any(re.search(p, q) for p in PERSONAL_PATTERNS)


def retrieve(question):
    """Find the closest chunks, keeping only one chunk per paper."""
    q_vec = embedder.encode([question], normalize_embeddings=True).tolist()
    res = collection.query(query_embeddings=q_vec, n_results=TOP_K * 3)

    sources, seen = [], set()
    for doc, meta, dist in zip(
        res["documents"][0], res["metadatas"][0], res["distances"][0]
    ):
        if meta["pmid"] in seen:
            continue
        seen.add(meta["pmid"])
        sources.append({"text": doc, "meta": meta, "distance": dist})
        if len(sources) == TOP_K:
            break
    return sources


def format_sources(sources):
    lines = []
    for i, s in enumerate(sources, 1):
        m = s["meta"]
        link = f"https://doi.org/{m['doi']}" if m["doi"] else f"https://pubmed.ncbi.nlm.nih.gov/{m['pmid']}/"
        lines.append(f"[{i}] {m['title']} ({m['year']}) - {link}")
    return "\n".join(lines)


def answer_question(question):
    """Returns (answer_text, sources_text)."""
    if is_personal_question(question):
        return (
            "I can't diagnose or give personal medical advice. Please talk to a "
            "doctor or other qualified health professional. I can share what "
            "research says about how epilepsy is diagnosed or treated, if that "
            "would help.",
            "",
        )

    sources = retrieve(question)
    if not sources or sources[0]["distance"] > MAX_DISTANCE:
        return "I couldn't find this in the available sources.", ""

    context = "\n\n".join(
        f"[{i}] {s['text']}" for i, s in enumerate(sources, 1)
    )
    prompt = f"SOURCES:\n{context}\n\nQUESTION: {question}"
    answer = None
    last_error = None
    for model_name in GEMINI_MODELS:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,
                    ),
                )
                answer = response.text
                break
            except Exception as e:
                last_error = e
                time.sleep(2 * (attempt + 1))
        if answer:
            break

    if not answer:
        return (
            "Sorry, the AI service is busy right now. Please try again in a "
            f"minute. ({last_error})",
            "",
        )

    if "couldn't find this in the available sources" in answer.lower():
        return answer, ""
    return answer, format_sources(sources)


if __name__ == "__main__":
    print(f"Epilepsy Research Assistant. {DISCLAIMER}")
    print("Type 'quit' to exit.\n")
    while True:
        q = input("Ask a question: ").strip()
        if q.lower() in ("quit", "exit", ""):
            break
        answer, srcs = answer_question(q)
        print(f"\n{answer}\n")
        if srcs:
            print("Sources:")
            print(srcs)
        print(f"\n({DISCLAIMER})\n")