from pathlib import Path

from app.rag.chunker import create_code_chunks


source_code = """
class UserService:

    def authenticate(self, username):
        return validate(username)

    def logout(self, username):
        return remove_session(username)


class PaymentService:

    def authenticate(self, user):
        return process_payment(user)


def health_check():
    return "ok"
"""


chunks = create_code_chunks(
    Path("example.py"),
    source_code,
)


for chunk in chunks:
    print(chunk)
    print("-" * 60)