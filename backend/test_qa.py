from app.rag.qa import ask_repository


result = ask_repository(
    repo_url=(
        "https://github.com/"
        "kaviprsanna03/Code-Sense-AI.git"
    ),
    question=(
        "Which function clones a GitHub repository, "
        "and how does it create the temporary workspace?"
    ),
)

print("\nAnswer:\n")
print(result["answer"])

print("\nSources:\n")

for source in result["sources"]:
    print(
        f"{source['file']}:"
        f"{source['start_line']}-"
        f"{source['end_line']} "
        f"(score={source['score']:.4f})"
    )