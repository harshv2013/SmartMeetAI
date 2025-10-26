import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "data/faiss_index.bin"
META_PATH = "data/metadata.json"

os.makedirs("data", exist_ok=True)

model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384

# --- Load existing FAISS index if available
if os.path.exists(INDEX_PATH):
    index = faiss.read_index(INDEX_PATH)
    print("✅ Loaded FAISS index from disk")
else:
    index = faiss.IndexFlatL2(dimension)
    print("🆕 Created new FAISS index")

# --- Load metadata
if os.path.exists(META_PATH):
    with open(META_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
else:
    docs = []

def add_document(doc_id, text, metadata):
    emb = model.encode([text])
    index.add(np.array(emb, dtype=np.float32))
    docs.append({"id": doc_id, "text": text, "metadata": metadata})

    # Save both index and metadata
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)


def semantic_search(query, n=5):
    """
    Perform hybrid semantic + keyword search with multi-term handling.
    Supports queries like 'Feifei and Beth' or 'training OR workshop'.
    Returns top unique results per meeting.
    """
    if index is None or len(docs) == 0:
        return []

    # 🔹 Split multi-term queries (by 'and', 'or', ',')
    subqueries = [q.strip() for part in query.lower().split(" and ") for q in part.split(",") if q.strip()]
    if not subqueries:
        subqueries = [query]

    results_map = {}

    for subq in subqueries:
        query_emb = model.encode([subq])
        query_emb = np.array(query_emb, dtype=np.float32)
        D, I = index.search(query_emb, n * 20)

        for rank, idx in enumerate(I[0]):
            if idx == -1 or idx >= len(docs):
                continue

            doc = docs[idx]
            meta = doc.get("metadata", {})
            meeting_id = meta.get("meeting_id")
            filename = meta.get("filename", "Unknown")

            if not meeting_id:
                continue

            text_chunk = doc["text"].strip()

            # ✅ Only keep if the subquery text appears (case-insensitive)
            if subq not in text_chunk.lower():
                continue

            if meeting_id not in results_map:
                snippet_start = max(0, text_chunk.lower().find(subq) - 60)
                snippet_end = snippet_start + 300
                snippet = text_chunk[snippet_start:snippet_end].replace("\n", " ") + "..."
                results_map[meeting_id] = {
                    "id": meeting_id,
                    "filename": filename,
                    "snippet": snippet,
                    "rank": rank,
                }

    # ✅ Sort by rank and remove duplicates
    results = sorted(results_map.values(), key=lambda x: x["rank"])
    return results[:n]
