import chromadb
from sentence_transformers import SentenceTransformer
 
model = SentenceTransformer("all-MiniLM-L6-v2")
collection = chromadb.PersistentClient(path="chroma_db").get_collection("epilepsy")
 
question = input("Ask a question: ")
q_vec = model.encode([question], normalize_embeddings=True).tolist()
 
results = collection.query(query_embeddings=q_vec, n_results=3)
 
for doc, meta, dist in zip(
    results["documents"][0], results["metadatas"][0], results["distances"][0]
):
    print(f"\n[{meta['year']}] {meta['title']}")
    print(f"  DOI: {meta['doi']}  |  distance: {dist:.3f} (lower = closer)")
    print(f"  {doc[:200]}...")
 