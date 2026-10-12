
from pathlib import Path

SOURCE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx"}

IGNORED_DIRECTORIES = {
    ".git", "node_modules", ".venv", "venv",
    "__pycache__", "dist", "build", ".next", "coverage",
}


def build_module_index(repo_path: Path) -> dict[str, Path]:
    """Index Python modules and JavaScript/TypeScript files."""
    repo_path = repo_path.resolve()
    module_index: dict[str, Path] = {}

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        relative_path = file_path.relative_to(repo_path)

        if any(part in IGNORED_DIRECTORIES for part in relative_path.parts):
            continue

        extension = file_path.suffix.lower()
        if extension not in SOURCE_EXTENSIONS:
            continue

        # Index JS/TS modules by repository-relative path.
        relative_key = relative_path.with_suffix("").as_posix()
        module_index[relative_key] = file_path

        if file_path.stem == "index":
            parent_key = relative_path.parent.as_posix()
            if parent_key != ".":
                module_index[parent_key] = file_path

        # Also index Python modules using dotted import names.
        if extension == ".py":
            parts = list(relative_path.parts)

            # Support common source layouts.
            if parts and parts[0] in {"backend", "src", "lib"}:
                parts = parts[1:]

            if file_path.name == "__init__.py":
                module_parts = parts[:-1]
            else:
                module_parts = parts[:-1] + [file_path.stem]

            module_name = ".".join(module_parts)
            if module_name:
                module_index[module_name] = file_path

    return module_index


def resolve_import(
    import_name: str,
    current_file: Path,
    repo_path: Path,
    module_index: dict[str, Path],
) -> Path | None:
    """Resolve local Python and relative JS/TS imports."""
    repo_path = repo_path.resolve()
    current_file = current_file.resolve()

    # Relative imports: ./App, ../utils/helper, etc.
    if import_name.startswith("."):
        base = (current_file.parent / import_name).resolve()

        candidates = [base]

        if not base.suffix:
            candidates.extend(
                base.with_suffix(ext)
                for ext in (".js", ".jsx", ".ts", ".tsx", ".py")
            )
            candidates.extend(
                base / f"index{ext}"
                for ext in (".js", ".jsx", ".ts", ".tsx")
            )

        for candidate in candidates:
            if not candidate.is_file():
                continue

            resolved = candidate.resolve()

            try:
                resolved.relative_to(repo_path)
            except ValueError:
                continue

            return resolved

        relative_key = (
            current_file.parent / import_name
        ).relative_to(repo_path).as_posix()

        return module_index.get(relative_key)

    # Absolute Python imports, e.g. app.parser or app.graph.
    return module_index.get(import_name)