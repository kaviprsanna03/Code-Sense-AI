from app.repository import clone_repository
from app.analyzer import analyze_repository
from app.graph import build_code_graph, get_dependents


repo_url = "https://github.com/pallets/flask.git"

repo_path = clone_repository(repo_url)

analysis_results = analyze_repository(repo_path)

graph = build_code_graph(
    analysis_results,
    repo_path,
)

target_file = str(
    repo_path / "src" / "flask" / "config.py"
)

dependents = get_dependents(
    graph,
    target_file,
)

print(f"\nTarget file:")
print(target_file)

print(f"\nFiles depending on config.py: {len(dependents)}")

for file_path in dependents:
    print(file_path)