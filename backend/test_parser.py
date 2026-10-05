from app.parser import parse_python_code


code = """
from .config import Config
from ..utils import helper
"""


tree = parse_python_code(code)

print(tree.root_node)

print("\nIMPORT NODES:")

for node in tree.root_node.children:
    if node.type == "import_from_statement":
        print("\n", node)

        for child in node.children:
            print(
                "type =", child.type,
                "| text =", child.text.decode("utf-8")
            )