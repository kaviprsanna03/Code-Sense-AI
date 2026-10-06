from app.repository import clone_repository
from app.import_resolver import (
    build_module_index,
    resolve_import,
)


repo_url = "https://github.com/pallets/flask.git"

repo_path = clone_repository(repo_url)

module_index = build_module_index(repo_path)

current_file = module_index["flask.app"]

tests = [
    "flask.config",
    "flask.testing",
    ".config",
    "does.not.exist",
]

for import_name in tests:
    resolved = resolve_import(
        import_name,
        current_file,
        repo_path,
        module_index,
    )

    print(f"{import_name} -> {resolved}")