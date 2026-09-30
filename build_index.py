import json
import chromadb
from sentence_transformers import SentenceTransformer

CHUNK_WORDS = 180   # max words per chunk
OVERLAP = 30        # words shared between neighbouring chunks


def chunk_text(text):
    """Split long text into overlapping pieces. Short text stays as one piece."""
    words = text.split()
    if len(words) <= CHUNK_WORDS:
        return [text]
    chunks = []
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + CHUNK_WORDS]))
        if start + CHUNK_WORDS >= len(words):
            break
        start += CHUNK_WORDS - OVERLAP
    return chunks


if __name__ == "__main__":
    with open("data/papers.json", encoding="utf-8") as f:
        papers = json.load(f)
    print(f"Loaded {len(papers)} papers")

    ids, docs, metas = [], [], []
    for p in papers:
        for i, chunk in enumerate(chunk_text(p["abstract"])):
            ids.append(f"{p['pmid']}_{i}")
            docs.append(f"{p['title']}. {chunk}")
            metas.append(
                {
                    "pmid": p["pmid"],
                    "title": p["title"],
                    "year": p["year"] or "",
                    "journal": p["journal"] or "",
                    "doi": p["doi"] or "",
                    "pub_types": ", ".join(p["pub_types"]),
                }
            )
    print(f"Created {len(docs)} chunks")

    print("Loading embedding model (first run downloads ~90 MB)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")

    print("Converting chunks to vectors...")
    embeddings = model.encode(
        docs, batch_size=64, show_progress_bar=True, normalize_embeddings=True
    )

    client = chromadb.PersistentClient(path="chroma_db")
    try:
        client.delete_collection("epilepsy")
    except Exception:
        pass
    collection = client.create_collection("epilepsy", metadata={"hnsw:space": "cosine"})

    for i in range(0, len(ids), 500):
        collection.add(
            ids=ids[i : i + 500],
            documents=docs[i : i + 500],
            metadatas=metas[i : i + 500],
            embeddings=embeddings[i : i + 500].tolist(),
        )
    print(f"Done. Stored {collection.count()} chunks in chroma_db/")