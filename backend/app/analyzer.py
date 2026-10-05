from pathlib import Path

from app.parser import parse_python_code, extract_code_structure


def analyze_file(file_path: Path) -> dict:
    source_code = file_path.read_text(
        encoding="utf-8",
        errors="ignore",
    )

    tree = parse_python_code(source_code)
    structure = extract_code_structure(tree)

    return {
        "file": str(file_path),
        "language": "python",
        **structure,
    }


def analyze_repository(repo_path: Path) -> list[dict]:
    results = []

    for file_path in repo_path.rglob("*.py"):
        result = analyze_file(file_path)
        results.append(result)

    return results