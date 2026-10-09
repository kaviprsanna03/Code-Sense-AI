from pathlib import Path

from app.rag.chunker import create_code_chunks
from app.rag.embedder import embed_text
from app.rag.vector_store import CodeVectorStore


source_code = '''
class UserService:
    def authenticate(self, username, password):
        """Validate user login credentials."""
        return username == "admin" and password == "secret"

    def logout(self, username):
        """End the user's active session."""
        return True


def calculate_total(prices):
    """Calculate the total price of all items."""
    return sum(prices)


def health_check():
    """Check whether the application is running."""
    return {"status": "healthy"}
'''

# 1. Parse actual Python source into code chunks
chunks = create_code_chunks(
    Path("sample_service.py"),
    source_code,
)

print(f"Code chunks created: {len(chunks)}")

# 2. Generate an embedding for every code chunk
embeddings = [
    embed_text(chunk["content"])
    for chunk in chunks
]

print(f"Embeddings created: {len(embeddings)}")

# 3. Store the embeddings in FAISS
store = CodeVectorStore(dimension=384)

store.add_chunks(chunks, embeddings)

print(f"Vectors stored in FAISS: {store.index.ntotal}")

# 4. Search using a natural-language question
query = "Which function checks if the application is healthy?"

query_embedding = embed_text(query)

results = store.search(
    query_embedding,
    top_k=3,
)

# 5. Display the most relevant code chunks
print(f"\nQuery: {query}")
print("\nTop matching code chunks:")

for rank, result in enumerate(results, start=1):
    metadata = result["metadata"]

    print(f"\n{rank}. {metadata['qualified_name']}")
    print(f"   Type: {metadata['type']}")
    print(f"   Similarity: {result['score']:.4f}")
    print(f"   Lines: {metadata['start_line']}-{metadata['end_line']}")
    print(f"   Code:\n{result['content']}")