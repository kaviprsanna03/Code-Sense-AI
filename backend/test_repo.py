from app.repository import clone_repository, discover_source_files


repo_url = "https://github.com/pallets/flask.git"

repo_path = clone_repository(repo_url)

print(f"\nRepository cloned to: {repo_path}")

source_files = discover_source_files(repo_path)

print(f"Found {len(source_files)} source files:\n")

for file in source_files[:20]:
    print(file)