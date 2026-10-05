import networkx as nx


def build_code_graph(analysis_results: list[dict]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for result in analysis_results:
        file_path = result["file"]

        graph.add_node(
            file_path,
            type="file",
            language=result["language"],
        )

        for imported in result["imports"]:
            graph.add_edge(
                file_path,
                imported,
                type="imports",
            )

        for class_name in result["classes"]:
            class_id = f"{file_path}::{class_name}"

            graph.add_node(
                class_id,
                type="class",
            )

            graph.add_edge(
                file_path,
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
                file_path,
                function_id,
                type="contains",
            )

    return graph