from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.repository import clone_repository
from app.analyzer import analyze_repository
from app.graph import build_code_graph


app = FastAPI(title="CodeSense AI")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def normalize_node_id(node_id: str, repo_path) -> str:
    parts = node_id.split("::", 1)

    relative_path = parts[0].replace(
        str(repo_path),
        "",
    ).lstrip("\\/")

    if len(parts) == 1:
        return relative_path.replace("\\", "/")

    return f"{relative_path.replace(chr(92), '/')}::{parts[1]}"


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/analyze")
def analyze_repository_endpoint(repo_url: str):
    repo_path = clone_repository(repo_url)

    analysis_results = analyze_repository(repo_path)

    graph = build_code_graph(
        analysis_results,
        repo_path,
    )

    nodes = [
        {
            "id": normalize_node_id(node, repo_path),
            "type": data.get("type"),
        }
        for node, data in graph.nodes(data=True)
    ]

    edges = [
        {
            "source": normalize_node_id(source, repo_path),
            "target": normalize_node_id(target, repo_path),
            "type": data.get("type"),
        }
        for source, target, data in graph.edges(data=True)
    ]

    return {
        "nodes": nodes,
        "edges": edges,
    }