from pathlib import Path

from tree_sitter import Language, Parser
import tree_sitter_python


PYTHON_LANGUAGE = Language(
    tree_sitter_python.language()
)

parser = Parser(PYTHON_LANGUAGE)


def create_code_chunks(
    file_path: Path,
    source_code: str,
) -> list[dict]:

    source_bytes = source_code.encode("utf-8")

    tree = parser.parse(source_bytes)

    chunks = []

    def get_node_name(node):
        name_node = node.child_by_field_name("name")

        if not name_node:
            return "<anonymous>"

        return name_node.text.decode("utf-8")

    def add_chunk(
        node,
        symbol,
        chunk_type,
        parent=None,
    ):

        content = source_bytes[
            node.start_byte:node.end_byte
        ].decode(
            "utf-8",
            errors="ignore",
        )

        qualified_name = symbol

        if parent:
            qualified_name = (
                f"{parent}.{symbol}"
            )

        chunks.append(
            {
                "content": content,
                "metadata": {
                    "file": str(file_path),
                    "language": "python",
                    "symbol": symbol,
                    "qualified_name": qualified_name,
                    "type": chunk_type,
                    "parent": parent,
                    "start_line": (
                        node.start_point[0] + 1
                    ),
                    "end_line": (
                        node.end_point[0] + 1
                    ),
                },
            }
        )

    def walk(node, parent_class=None):

        if node.type == "class_definition":

            class_name = get_node_name(node)

            add_chunk(
                node=node,
                symbol=class_name,
                chunk_type="class",
            )

            for child in node.named_children:

                walk(
                    child,
                    parent_class=class_name,
                )

            return

        if node.type == "function_definition":

            function_name = get_node_name(node)

            if parent_class:

                add_chunk(
                    node=node,
                    symbol=function_name,
                    chunk_type="method",
                    parent=parent_class,
                )

            else:

                add_chunk(
                    node=node,
                    symbol=function_name,
                    chunk_type="function",
                )

            return

        for child in node.named_children:
            walk(
                child,
                parent_class=parent_class,
            )

    walk(tree.root_node)

    return chunks