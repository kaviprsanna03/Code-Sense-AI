
from tree_sitter import Language, Parser
import tree_sitter_python
import tree_sitter_javascript
import tree_sitter_typescript


# Supported language grammars
LANGUAGES = {
    ".py": Language(tree_sitter_python.language()),
    ".js": Language(tree_sitter_javascript.language()),
    ".jsx": Language(tree_sitter_javascript.language()),
    ".ts": Language(tree_sitter_typescript.language_typescript()),
    ".tsx": Language(tree_sitter_typescript.language_tsx()),
}


def get_parser(extension: str) -> Parser:
    """Return a Tree-sitter parser for the file extension."""
    extension = extension.lower()
    language = LANGUAGES.get(extension)

    if language is None:
        raise ValueError(f"Unsupported source extension: {extension}")

    return Parser(language)


def parse_code(source_code: str, extension: str):
    """Parse source code using its language grammar."""
    parser = get_parser(extension)
    return parser.parse(source_code.encode("utf-8"))


def parse_python_code(source_code: str):
    """Backward-compatible Python parser."""
    return parse_code(source_code, ".py")


def extract_code_structure(
    tree,
    extension: str = ".py",
) -> dict:
    """
    Extract imports, classes, functions and calls
    from a parsed Python, JavaScript, JSX, TypeScript
    or TSX syntax tree.
    """
    extension = extension.lower()

    imports = []
    classes = []
    functions = []
    calls = []

    def text(node):
        return node.text.decode("utf-8", errors="replace")

    def walk(node):
        kind = node.type

        # --------------------------------------------
        # PYTHON
        # --------------------------------------------
        if extension == ".py":

            if kind == "import_from_statement":
                module = node.child_by_field_name("module_name")

                if module:
                    imports.append(text(module))

            elif kind == "import_statement":
                for child in node.named_children:
                    if child.type == "dotted_name":
                        imports.append(text(child))

            elif kind == "class_definition":
                name = node.child_by_field_name("name")

                if name:
                    classes.append(text(name))

            elif kind == "function_definition":
                name = node.child_by_field_name("name")

                if name:
                    functions.append(text(name))

            elif kind == "call":
                function = node.child_by_field_name("function")

                if function:
                    calls.append(text(function))

        # --------------------------------------------
        # JAVASCRIPT / JSX / TYPESCRIPT / TSX
        # --------------------------------------------
        else:

            # Import declarations and re-exports
            if kind in {"import_statement", "export_statement"}:
                source_node = node.child_by_field_name("source")

                if source_node:
                    source = text(source_node).strip("\"'")
                    imports.append(source)

            # Class declarations
            elif kind == "class_declaration":
                name = node.child_by_field_name("name")

                if name:
                    classes.append(text(name))

            # Function declarations
            elif kind in {
                "function_declaration",
                "generator_function_declaration",
            }:
                name = node.child_by_field_name("name")

                if name:
                    functions.append(text(name))

            # Function calls
            elif kind == "call_expression":
                function = node.child_by_field_name("function")

                if function:
                    calls.append(text(function))

            # Arrow functions and function expressions
            elif kind in {
                "lexical_declaration",
                "variable_declaration",
            }:
                for declarator in node.named_children:

                    if declarator.type != "variable_declarator":
                        continue

                    name = declarator.child_by_field_name("name")
                    value = declarator.child_by_field_name("value")

                    if (
                        name
                        and value
                        and value.type in {
                            "arrow_function",
                            "function_expression",
                            "generator_function",
                        }
                    ):
                        functions.append(text(name))

        # Visit all child nodes
        for child in node.children:
            walk(child)

    walk(tree.root_node)

    # Remove duplicates while preserving order
    return {
        "imports": list(dict.fromkeys(imports)),
        "classes": list(dict.fromkeys(classes)),
        "functions": list(dict.fromkeys(functions)),
        "calls": list(dict.fromkeys(calls)),
    }
