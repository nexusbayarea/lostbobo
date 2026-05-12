import numpy as np


class VectorStore:
    def __init__(self):
        self.records: list[tuple[np.ndarray, str, object]] = []

    def insert(self, memory, embedding: list[float]):
        emb = np.array(embedding)
        self.records.append((emb, memory.memory_id, memory))

    def search(self, query_embedding: list[float], limit: int = 10) -> list:
        if not self.records:
            return []
        query = np.array(query_embedding)
        scores = []
        for emb, _mid, mem in self.records:
            norm_q = np.linalg.norm(query)
            norm_emb = np.linalg.norm(emb)
            sim = np.dot(query, emb) / (norm_q * norm_emb + 1e-8)
            mem.metadata["_similarity"] = float(sim)
            scores.append((sim, mem))
        scores.sort(key=lambda x: x[0], reverse=True)
        return [mem for _, mem in scores[:limit]]
