from pathlib import Path
import subprocess
import tempfile


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
}


def clone_repository(repo_url: str) -> Path:
    workspace = Path(tempfile.mkdtemp(prefix="codesense_"))

    subprocess.run(
        [
            "git",
            "clone",
            "--depth",
            "1",
            repo_url,
            str(workspace),
        ],
        check=True,
        timeout=60,
    )

    return workspace


def discover_source_files(repo_path: Path) -> list[Path]:
    source_files = []

    for path in repo_path.rglob("*"):

        if not path.is_file():
            continue

        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue

        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        source_files.append(path)

    return source_files