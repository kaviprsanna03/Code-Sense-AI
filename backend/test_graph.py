from app.repository import clone_repository
from app.analyzer import analyze_repository
from app.graph import build_code_graph


repo_url = "https://github.com/pallets/flask.git"

repo_path = clone_repository(repo_url)

analysis_results = analyze_repository(repo_path)

graph = build_code_graph(analysis_results)

print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")

print("\nFirst 10 nodes:")

for node, data in list(graph.nodes(data=True))[:10]:
    print(node, data)

print("\nFirst 10 edges:")

for source, target, data in list(graph.edges(data=True))[:10]:
    print(source, "→", target, data)