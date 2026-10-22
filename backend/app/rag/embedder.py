
from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "all-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Load the embedding model only when first needed."""
    return SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )


def embed_text(text: str) -> list[float]:
    vector = get_model().encode(
        text,
        convert_to_numpy=True,
        show_progress_bar=False,
    )
    return vector.tolist()


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    vectors = get_model().encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=False,
        batch_size=8,
    )

    return vectors.tolist()
