from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def embed_text(text: str) -> list[float]:
    vector = model.encode(text)
    return vector.tolist()


def embed_texts(
    texts: list[str],
) -> list[list[float]]:
    if not texts:
        return []

    vectors = model.encode(
        texts,
        convert_to_numpy=True,
        show_progress_bar=True,
    )

    return vectors.tolist()