import { useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import "./App.css";


function App() {
  const [repoUrl, setRepoUrl] = useState("");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function analyzeRepository() {
    if (!repoUrl.trim()) {
      setError("Enter a GitHub repository URL.");
      return;
    }

    setLoading(true);
    setError("");
    setSelectedNode(null);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/analyze?repo_url=${encodeURIComponent(repoUrl)}`
      );

      if (!response.ok) {
        throw new Error("Repository analysis failed.");
      }

      const data = await response.json();

      const fileNodes = data.nodes
        .filter((node) => node.type === "file")
        .map((node, index) => ({
          id: node.id,
          position: {
            x: (index % 5) * 220,
            y: Math.floor(index / 5) * 120,
          },
          data: {
            label: node.id,
          },
        }));

      const nodeIds = new Set(
        fileNodes.map((node) => node.id)
      );

      const fileEdges = data.edges
        .filter(
          (edge) =>
            edge.type === "imports" &&
            nodeIds.has(edge.source) &&
            nodeIds.has(edge.target)
        )
        .map((edge, index) => ({
          id: `edge-${index}`,
          source: edge.source,
          target: edge.target,
        }));

      setNodes(fileNodes);
      setEdges(fileEdges);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleNodeClick(event, node) {
    setSelectedNode(node);
  }

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>CodeSense AI</h1>
          <p>Understand your codebase.</p>
        </div>

        <div className="repo-controls">
          <input
            type="text"
            placeholder="GitHub repository URL"
            value={repoUrl}
            onChange={(event) => setRepoUrl(event.target.value)}
          />

          <button
            className="analyze-button"
            onClick={analyzeRepository}
            disabled={loading}
          >
            {loading ? "Analyzing..." : "Analyze Repository"}
          </button>
        </div>
      </header>

      <main className="workspace">
        <section className="graph-panel">

          <div className="panel-header">
            <h2>Repository Architecture</h2>

            <span>
              {nodes.length} files · {edges.length} dependencies
            </span>
          </div>

          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          <div className="graph-container">

            {nodes.length === 0 ? (
              <div className="placeholder-content">
                <div className="placeholder-icon">
                  ⌘
                </div>

                <h3>Architecture Map</h3>

                <p>
                  Enter a GitHub repository above to
                  visualize its structure and dependencies.
                </p>
              </div>
            ) : (
              <ReactFlow
                nodes={nodes}
                edges={edges}
                fitView
                onNodeClick={handleNodeClick}
                nodesConnectable={false}
              >
                <Background />
                <Controls />
                <MiniMap />
              </ReactFlow>
            )}

            {selectedNode && (
              <aside className="node-details">

                <button
                  className="close-button"
                  onClick={() => setSelectedNode(null)}
                >
                  ×
                </button>

                <p className="details-label">
                  FILE
                </p>

                <h3>
                  {selectedNode.data.label}
                </h3>

                <div className="details-section">
                  <span>Type</span>
                  <strong>
                    file
                  </strong>
                </div>

                <div className="details-section">
                  <span>Node ID</span>
                  <code>
                    {selectedNode.id}
                  </code>
                </div>

              </aside>
            )}

          </div>

        </section>
      </main>
    </div>
  );
}

export default App;