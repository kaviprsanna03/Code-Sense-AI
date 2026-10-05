from app.parser import parse_python_code, extract_code_structure


code = """
from database import connect

class UserService:
    def get_user(self, user_id):
        return connect(user_id)
"""


tree = parse_python_code(code)

structure = extract_code_structure(tree)

print(structure)