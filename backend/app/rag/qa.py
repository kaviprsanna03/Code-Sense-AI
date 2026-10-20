from app.rag.embedder import embed_text
from app.rag.indexer import build_repository_index
from app.rag.llm import generate_answer


def ask_repository(
    repo_url: str,
    question: str,
) -> dict:

    # 1. Index the repository
    store, stats = build_repository_index(repo_url)

    # 2. Retrieve relevant code
    results = store.search(
        embed_text(question),
        top_k=5,
    )

    # 3. Build evidence for the LLM
    context_parts = []

    sources = []

    for result in results:
        metadata = result["metadata"]

        file_path = metadata["file"]
        start_line = metadata["start_line"]
        end_line = metadata["end_line"]

        context_parts.append(
            f"File: {file_path}\n"
            f"Lines: {start_line}-{end_line}\n"
            f"Code:\n{result['content']}"
        )

        sources.append(
            {
                "file": file_path,
                "start_line": start_line,
                "end_line": end_line,
                "score": result["score"],
            }
        )

    context = "\n\n---\n\n".join(context_parts)

    # 4. Generate an answer from retrieved evidence
    if not results:
        answer = (
            "I couldn't find relevant code in the indexed "
            "Python files to answer this question."
        )
    else:
        answer = generate_answer(
            question=question,
            context=context,
        )

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "index_stats": stats,
    }