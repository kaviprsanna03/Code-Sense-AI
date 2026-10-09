import faiss
import numpy as np


class CodeVectorStore:
    def __init__(self, dimension: int = 384):
        self.dimension = dimension

        self.index = faiss.IndexFlatIP(dimension)

        self.chunks = []

    def add_chunks(
        self,
        chunks: list[dict],
        embeddings: list[list[float]],
    ) -> None:
        if not chunks:
            return

        vectors = np.asarray(
            embeddings,
            dtype=np.float32,
        )

        if vectors.ndim != 2:
            raise ValueError(
                "Embeddings must be a 2D array."
            )

        if vectors.shape != (
            len(chunks),
            self.dimension,
        ):
            raise ValueError(
                "Embedding dimensions or chunk count mismatch."
            )

        faiss.normalize_L2(vectors)

        self.index.add(vectors)

        self.chunks.extend(chunks)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[dict]:
        if top_k <= 0:
            raise ValueError(
                "top_k must be greater than zero."
            )

        if not self.chunks:
            return []

        query_vector = np.asarray(
            [query_embedding],
            dtype=np.float32,
        )

        if query_vector.shape[1] != self.dimension:
            raise ValueError(
                "Query embedding dimension mismatch."
            )

        faiss.normalize_L2(query_vector)

        scores, indices = self.index.search(
            query_vector,
            min(top_k, len(self.chunks)),
        )

        results = []

        for score, idx in zip(
            scores[0],
            indices[0],
        ):
            if idx == -1:
                continue

            results.append(
                {
                    "score": float(score),
                    "content": self.chunks[idx]["content"],
                    "metadata": self.chunks[idx]["metadata"],
                }
            )

        return results