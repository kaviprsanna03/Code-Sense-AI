
from pathlib import Path

from app.parser import parse_code, extract_code_structure


SUPPORTED_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "dist",
    "build",
    ".next",
    "coverage",
}


def analyze_file(
    file_path: Path,
    repo_path: Path | None = None,
) -> dict:
    source_code = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    extension = file_path.suffix.lower()

    tree = parse_code(source_code, extension)
    structure = extract_code_structure(tree, extension)

    language_map = {
        ".py": "python",
        ".js": "javascript",
        ".jsx": "javascript",
        ".ts": "typescript",
        ".tsx": "typescript",
    }

    return {
        "file": file_path,
        "relative_path": (
            str(file_path.relative_to(repo_path))
            if repo_path
            else str(file_path)
        ),
        "language": language_map[extension],
        **structure,
    }


def analyze_repository(repo_path: Path) -> list[dict]:
    results = []

    for file_path in repo_path.rglob("*"):
        if not file_path.is_file():
            continue

        # Skip generated directories and virtual environments.
        if any(
            part in IGNORED_DIRECTORIES
            for part in file_path.relative_to(repo_path).parts
        ):
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            result = analyze_file(file_path, repo_path)
            results.append(result)

        except (OSError, ValueError) as exc:
            print(f"Skipping {file_path}: {exc}")

    return results
