from app.repository import clone_repository, discover_source_files
from app.analyzer import analyze_repository


repo_url = "https://github.com/pallets/flask.git"

repo_path = clone_repository(repo_url)

results = analyze_repository(repo_path)

print(f"\nAnalyzed {len(results)} Python files.\n")

for result in results[:5]:
    print("=" * 60)
    print(f"FILE: {result['file']}")
    print(f"IMPORTS: {result['imports']}")
    print(f"CLASSES: {result['classes']}")
    print(f"FUNCTIONS: {result['functions']}")
    print(f"CALLS: {result['calls']}")