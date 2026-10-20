from app.rag.llm import generate_answer


question = "What is CodeSense AI?"
context = """
CodeSense AI analyzes software repositories.
It builds code dependency graphs and retrieves
relevant source code using semantic search.
"""

answer = generate_answer(
    question=question,
    context=context,
)

print("\nCodeSense AI response:\n")
print(answer)