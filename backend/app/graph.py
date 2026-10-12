
from pathlib import Path

import networkx as nx

from app.import_resolver import (
    build_module_index,
    resolve_import,
)


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


def add_package_hierarchy(
    graph: nx.DiGraph,
    file_path: Path,
    repo_path: Path,
):
    relative_path = file_path.relative_to(repo_path)
    directory_parts = list(relative_path.parent.parts)

    if not directory_parts:
        return

    current_path = repo_path
    previous_package = None

    for part in directory_parts:
        current_path = current_path / part
        package_id = str(current_path)

        graph.add_node(
            package_id,
            type="package",
            name=part,
        )

        if previous_package is not None:
            graph.add_edge(
                previous_package,
                package_id,
                type="contains",
            )

        previous_package = package_id

    if previous_package is not None:
        graph.add_edge(
            previous_package,
            str(file_path),
            type="contains",
        )


def build_code_graph(
    analysis_results: list[dict],
    repo_path: Path,
) -> nx.DiGraph:
    graph = nx.DiGraph()
    repo_path = repo_path.resolve()

    module_index = build_module_index(repo_path)

    for result in analysis_results:
        file_path = Path(result["file"]).resolve()
        file_id = str(file_path)

        # File node
        graph.add_node(
            file_id,
            type="file",
            name=file_path.name,
            language=result.get("language", "unknown"),
        )

        # Folder/package hierarchy
        add_package_hierarchy(
            graph,
            file_path,
            repo_path,
        )

        # Import relationships
        for imported in result.get("imports", []):
            resolved_file = resolve_import(
                imported,
                file_path,
                repo_path,
                module_index,
            )

            if resolved_file is None:
                continue

            resolved_file = Path(resolved_file).resolve()

            if resolved_file == file_path:
                continue

            if resolved_file not in {
                Path(item["file"]).resolve()
                for item in analysis_results
            }:
                continue

            graph.add_edge(
                file_id,
                str(resolved_file),
                type="imports",
            )

        # Classes and functions
        for class_name in result.get("classes", []):
            class_id = f"{file_id}::{class_name}"

            graph.add_node(
                class_id,
                type="class",
                name=class_name,
            )

            graph.add_edge(
                file_id,
                class_id,
                type="contains",
            )

        for function_name in result.get("functions", []):
            function_id = f"{file_id}::{function_name}"

            graph.add_node(
                function_id,
                type="function",
                name=function_name,
            )

            graph.add_edge(
                file_id,
                function_id,
                type="contains",
            )

    return graph


def get_dependents(
    graph: nx.DiGraph,
    file_path: str,
) -> list[str]:
    return [
        predecessor
        for predecessor in graph.predecessors(file_path)
        if graph.edges[predecessor, file_path].get("type") == "imports"
    ]
