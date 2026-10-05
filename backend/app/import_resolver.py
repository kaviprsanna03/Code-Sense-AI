from pathlib import Path


def build_module_index(repo_path: Path) -> dict[str, Path]:
    module_index = {}

    for file_path in repo_path.rglob("*.py"):
        relative_path = file_path.relative_to(repo_path)

        if relative_path.parts[0] in {"src", "lib"}:
            module_parts = relative_path.parts[1:]
        else:
            module_parts = relative_path.parts

        if file_path.name == "__init__.py":
            module_name = ".".join(module_parts[:-1])
        else:
            module_name = ".".join(module_parts).removesuffix(".py")

        module_index[module_name] = file_path

    return module_index


def resolve_import(
    import_name: str,
    current_file: Path,
    repo_path: Path,
    module_index: dict[str, Path],
) -> Path | None:

    if not import_name.startswith("."):
        return module_index.get(import_name)

    level = len(import_name) - len(import_name.lstrip("."))

    module_name = import_name.lstrip(".")

    relative_file = current_file.relative_to(repo_path)

    package_parts = list(relative_file.parent.parts)

    if package_parts and package_parts[0] in {"src", "lib"}:
        package_parts = package_parts[1:]

    base_parts = package_parts[:len(package_parts) - (level - 1)]

    if module_name:
        base_parts.extend(module_name.split("."))

    resolved_module = ".".join(base_parts)

    return module_index.get(resolved_module)