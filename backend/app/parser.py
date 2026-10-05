from tree_sitter import Language, Parser
import tree_sitter_python


PYTHON_LANGUAGE = Language(tree_sitter_python.language())

parser = Parser(PYTHON_LANGUAGE)


def parse_python_code(source_code: str):
    source_bytes = source_code.encode("utf-8")
    return parser.parse(source_bytes)


def extract_code_structure(tree):
    imports = []
    classes = []
    functions = []
    calls = []

    def walk(node):
        if node.type == "import_from_statement":
            imports.append(node.text.decode("utf-8"))

        elif node.type == "import_statement":
            imports.append(node.text.decode("utf-8"))

        elif node.type == "class_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                classes.append(name_node.text.decode("utf-8"))

        elif node.type == "function_definition":
            name_node = node.child_by_field_name("name")
            if name_node:
                functions.append(name_node.text.decode("utf-8"))

        elif node.type == "call":
            function_node = node.child_by_field_name("function")
            if function_node:
                calls.append(function_node.text.decode("utf-8"))

        for child in node.children:
            walk(child)

    walk(tree.root_node)

    return {
        "imports": imports,
        "classes": classes,
        "functions": functions,
        "calls": calls,
    }