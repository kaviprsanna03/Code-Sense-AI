from app.rag.indexer import build_repository_index
from app.rag.embedder import embed_text


REPO_URL = (
    "https://github.com/"
    "kaviprsanna03/Code-Sense-AI.git"
)


# 1. Build an index from a real GitHub repository
store, stats = build_repository_index(REPO_URL)

print("\nRepository indexing results:")

for name, value in stats.items():
    print(f"{name}: {value}")


# 2. Ask a natural-language question
query = (
    "Which function clones a GitHub repository "
    "into a temporary workspace?"
)

# 3. Retrieve the most relevant code
results = store.search(
    embed_text(query),
    top_k=5,
)

print(f"\nQuery: {query}")
print("\nRetrieved code:")

for rank, result in enumerate(results, start=1):
    metadata = result["metadata"]

    print(f"\n{rank}. {metadata['qualified_name']}")
    print(f"   File: {metadata['file']}")
    print(f"   Similarity: {result['score']:.4f}")
    print(f"   Code:\n{result['content']}")