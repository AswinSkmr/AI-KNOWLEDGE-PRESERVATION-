"""FAISS index management — a single flat index shared across all documents."""
import os
import threading

import faiss
import numpy as np

INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "vector_index/documents.index")
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2's fixed output size

_lock = threading.Lock()
_index: faiss.Index | None = None


def get_index() -> faiss.Index:
    global _index
    if _index is None:
        if os.path.exists(INDEX_PATH):
            _index = faiss.read_index(INDEX_PATH)
        else:
            _index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
    return _index


def save_index() -> None:
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(get_index(), INDEX_PATH)


def add_vectors(vectors: list[list[float]]) -> list[int]:
    with _lock:
        index = get_index()
        start_position = index.ntotal
        array = np.array(vectors, dtype="float32")
        index.add(array)
        save_index()
        return list(range(start_position, start_position + len(vectors)))


def search(query_vector: list[float], top_k: int) -> tuple[list[float], list[int]]:
    index = get_index()
    if index.ntotal == 0:
        return [], []
    array = np.array([query_vector], dtype="float32")
    scores, positions = index.search(array, min(top_k, index.ntotal))
    return scores[0].tolist(), positions[0].tolist()