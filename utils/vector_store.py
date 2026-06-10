"""
Vector Store
Embeddings via sentence-transformers, index via FAISS.
"""

import os
import json
import pickle
import numpy as np
from typing import List, Dict, Any, Optional


class VectorStore:
    def __init__(self, persist_dir: str = "data/vectorstore"):
        self.persist_dir = persist_dir
        os.makedirs(persist_dir, exist_ok=True)

        self._index   = None
        self._chunks  : List[Dict[str, Any]] = []
        self._embedder = None

        self._load_embedder()
        self._load_index()

    # ── Embedder ──────────────────────────────────────────────────────────────
    def _load_embedder(self):
        try:
            from sentence_transformers import SentenceTransformer
            self._embedder = SentenceTransformer("all-MiniLM-L6-v2")
        except ImportError:
            raise ImportError(
                "sentence-transformers not installed. Run: pip install sentence-transformers"
            )

    def _embed(self, texts: List[str]) -> np.ndarray:
        return self._embedder.encode(texts, convert_to_numpy=True, show_progress_bar=False)

    # ── Persistence ───────────────────────────────────────────────────────────
    def _index_path(self):  return os.path.join(self.persist_dir, "faiss.index")
    def _meta_path(self):   return os.path.join(self.persist_dir, "chunks.pkl")

    def _load_index(self):
        if os.path.exists(self._index_path()) and os.path.exists(self._meta_path()):
            try:
                import faiss
                self._index = faiss.read_index(self._index_path())
                with open(self._meta_path(), "rb") as f:
                    self._chunks = pickle.load(f)
            except Exception:
                self._index  = None
                self._chunks = []

    def _save_index(self):
        import faiss
        if self._index is not None:
            faiss.write_index(self._index, self._index_path())
            with open(self._meta_path(), "wb") as f:
                pickle.dump(self._chunks, f)

    # ── Public API ────────────────────────────────────────────────────────────
    def add_documents(self, chunks: List[Dict[str, Any]]):
        import faiss

        texts      = [c["content"] for c in chunks]
        embeddings = self._embed(texts).astype("float32")
        dim        = embeddings.shape[1]

        if self._index is None:
            self._index = faiss.IndexFlatL2(dim)

        self._index.add(embeddings)
        self._chunks.extend(chunks)
        self._save_index()

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        if self._index is None or self._index.ntotal == 0:
            return []

        q_emb = self._embed([query]).astype("float32")
        k     = min(k, self._index.ntotal)
        distances, indices = self._index.search(q_emb, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self._chunks):
                results.append({
                    "content"  : self._chunks[idx]["content"],
                    "metadata" : self._chunks[idx]["metadata"],
                    "score"    : float(dist),
                })
        return results

    def get_doc_chunks(self, doc_name: str) -> List[Dict[str, Any]]:
        return [c for c in self._chunks if c["metadata"].get("source") == doc_name]

    def clear(self):
        self._index  = None
        self._chunks = []
        for p in [self._index_path(), self._meta_path()]:
            if os.path.exists(p):
                os.remove(p)
