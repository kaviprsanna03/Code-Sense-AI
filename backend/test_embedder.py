from app.rag.embedder import embed_text

from sentence_transformers import util


text_a = """
User authentication validates login credentials.
"""

text_b = """
The login system checks the user's password.
"""

text_c = """
The application loads records from the database.
"""


vector_a = embed_text(text_a)
vector_b = embed_text(text_b)
vector_c = embed_text(text_c)


similarity_ab = util.cos_sim(
    vector_a,
    vector_b,
)

similarity_ac = util.cos_sim(
    vector_a,
    vector_c,
)


print("A ↔ B:", similarity_ab.item())
print("A ↔ C:", similarity_ac.item())