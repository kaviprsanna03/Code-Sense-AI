from app.repository import (
    clone_repository,
    discover_source_files,
)

from app.rag.chunker import create_code_chunks
from app.rag.embedder import embed_texts
from app.rag.vector_store import CodeVectorStore


def build_repository_index(
    repo_url: str,
) -> tuple[CodeVectorStore, dict]:

    # 1. Clone the repository
    repo_path = clone_repository(repo_url)

    # 2. Discover supported source files
    discovered_files = discover_source_files(repo_path)

    # The current chunker supports Python syntax only.
    python_files = [
        path
        for path in discovered_files
        if path.suffix.lower() == ".py"
    ]

    all_chunks = []
    files_read = 0
    skipped_files = 0

    # 3. Read files and extract code chunks
    for file_path in python_files:
        try:
            source_code = file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )
        except OSError:
            skipped_files += 1
            continue

        relative_path = file_path.relative_to(repo_path)

        chunks = create_code_chunks(
            relative_path,
            source_code,
        )

        all_chunks.extend(chunks)
        files_read += 1

    # 4. Generate embeddings and build the vector index
    store = CodeVectorStore()

    if all_chunks:
        embeddings = embed_texts(
            [
                chunk["content"]
                for chunk in all_chunks
            ]
        )

        store.add_chunks(
            all_chunks,
            embeddings,
        )

    # 5. Return the index and useful statistics
    stats = {
        "files_discovered": len(discovered_files),
        "python_files_found": len(python_files),
        "files_read": files_read,
        "files_skipped": skipped_files,
        "chunks_created": len(all_chunks),
        "vectors_indexed": store.index.ntotal,
    }

    return store, stats