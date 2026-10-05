import networkx as nx

from app.import_resolver import build_module_index, resolve_import


def build_code_graph(
    analysis_results: list[dict],
    repo_path,
) -> nx.DiGraph:

    graph = nx.DiGraph()

    module_index = build_module_index(repo_path)

    for result in analysis_results:
        file_path = result["file"]

        graph.add_node(
            str(file_path),
            type="file",
            language=result["language"],
        )

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
                str(file_path),
                str(resolved_file),
                type="imports",
            )

        for class_name in result["classes"]:
            class_id = f"{file_path}::{class_name}"

            graph.add_node(
                class_id,
                type="class",
            )

            graph.add_edge(
                str(file_path),
                class_id,
                type="contains",
            )

        for function_name in result["functions"]:
            function_id = f"{file_path}::{function_name}"

            graph.add_node(
                function_id,
                type="function",
            )

            graph.add_edge(
                str(file_path),
                function_id,
                type="contains",
            )

    return graph

def get_dependents(
    graph: nx.DiGraph,
    file_path: str,
) -> list[str]:
    return list(graph.predecessors(file_path))