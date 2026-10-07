import networkx as nx

from app.import_resolver import (
    build_module_index,
    resolve_import,
)


def add_package_hierarchy(
    graph: nx.DiGraph,
    file_path,
    repo_path,
):
    relative_path = file_path.relative_to(repo_path)

    directory_parts = list(
        relative_path.parent.parts
    )

    # Ignore the repository root.
    if not directory_parts:
        return

    # Build package hierarchy from the
    # source directory down to the file's parent.
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

    # Connect the deepest package to the file.
    if previous_package is not None:
        graph.add_edge(
            previous_package,
            str(file_path),
            type="contains",
        )


def build_code_graph(
    analysis_results: list[dict],
    repo_path,
) -> nx.DiGraph:

    graph = nx.DiGraph()

    module_index = build_module_index(
        repo_path
    )

    for result in analysis_results:

        file_path = result["file"]

        file_id = str(file_path)

        # --------------------------------------------------
        # FILE NODE
        # --------------------------------------------------

        graph.add_node(
            file_id,
            type="file",
            name=file_path.name,
            language=result["language"],
        )

        # --------------------------------------------------
        # PACKAGE HIERARCHY
        # --------------------------------------------------

        add_package_hierarchy(
            graph,
            file_path,
            repo_path,
        )

        # --------------------------------------------------
        # IMPORT RELATIONSHIPS
        # --------------------------------------------------

        for imported in result["imports"]:

            resolved_file = resolve_import(
                imported,
                file_path,
                repo_path,
                module_index,
            )

            if resolved_file is None:
                continue

            if resolved_file == file_path:
                continue

            graph.add_edge(
                file_id,
                str(resolved_file),
                type="imports",
            )

        # --------------------------------------------------
        # CLASS NODES
        # --------------------------------------------------

        for class_name in result["classes"]:

            class_id = (
                f"{file_path}::{class_name}"
            )

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

        # --------------------------------------------------
        # FUNCTION NODES
        # --------------------------------------------------

        for function_name in result["functions"]:

            function_id = (
                f"{file_path}::{function_name}"
            )

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

    return list(
        graph.predecessors(file_path)
    )