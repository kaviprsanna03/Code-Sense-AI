import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { useMemo, useState } from "react";

import {
  ReactFlow,
  Background,
  Controls,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";


function App() {
  const [repoUrl, setRepoUrl] = useState("");

  const [graphData, setGraphData] = useState({
    nodes: [],
    edges: [],
  });

  const [selectedNode, setSelectedNode] =
    useState(null);

  const [expandedNodes, setExpandedNodes] =
    useState(new Set());

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  // AI codebase Q&A
  const [question, setQuestion] = useState("");
  const [qaLoading, setQaLoading] = useState(false);
  const [qaError, setQaError] = useState("");
  const [qaResult, setQaResult] = useState(null);


  // =====================================================
  // ANALYZE REPOSITORY
  // =====================================================

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
        `http://127.0.0.1:8000/analyze?repo_url=${encodeURIComponent(
          repoUrl
        )}`
      );

      if (!response.ok) {
        throw new Error(
          "Repository analysis failed."
        );
      }

      const data = await response.json();

      setGraphData(data);


      // Find top-level packages.
      const packageNodes =
        data.nodes.filter(
          (node) =>
            node.type === "package"
        );


      const childIds = new Set(
        data.edges
          .filter(
            (edge) =>
              edge.type === "contains"
          )
          .map(
            (edge) =>
              edge.target
          )
      );


      const rootPackages =
        packageNodes.filter(
          (node) =>
            !childIds.has(node.id)
        );


      setExpandedNodes(
        new Set(
          rootPackages.map(
            (node) =>
              node.id
          )
        )
      );

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }


  // =====================================================
  // ASK QUESTIONS ABOUT THE REPOSITORY
  // =====================================================

  async function askRepository() {
    if (!repoUrl.trim()) {
      setQaError("Enter a GitHub repository URL first.");
      return;
    }

    if (!question.trim()) {
      setQaError("Enter a question about the codebase.");
      return;
    }

    setQaLoading(true);
    setQaError("");
    setQaResult(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          repo_url: repoUrl.trim(),
          question: question.trim(),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        const detail = typeof data.detail === "string"
          ? data.detail
          : "Unable to answer your question.";
        throw new Error(detail);
      }

      setQaResult(data);
    } catch (err) {
      setQaError(
        err.message || "Could not connect to the CodeSense backend."
      );
    } finally {
      setQaLoading(false);
    }
  }


  // =====================================================
  // BUILD ARCHITECTURE TREE
  // =====================================================

  const architecture = useMemo(() => {

    const relevantNodes =
      graphData.nodes.filter(
        (node) =>
          node.type === "package" ||
          node.type === "file"
      );


    const nodeMap = new Map(
      relevantNodes.map(
        (node) => [
          node.id,
          {
            ...node,
            children: [],
          },
        ]
      )
    );


    const parentMap = new Map();


    graphData.edges
      .filter(
        (edge) =>
          edge.type === "contains" &&
          nodeMap.has(edge.source) &&
          nodeMap.has(edge.target)
      )
      .forEach((edge) => {

        const parent =
          nodeMap.get(
            edge.source
          );

        const child =
          nodeMap.get(
            edge.target
          );

        parent.children.push(
          child
        );

        parentMap.set(
          child.id,
          parent.id
        );

      });


    const roots =
      relevantNodes
        .filter(
          (node) =>
            !parentMap.has(
              node.id
            )
        )
        .map(
          (node) =>
            nodeMap.get(
              node.id
            )
        );


    function sortTree(nodes) {

      nodes.sort((a, b) => {

        if (
          a.type !== b.type
        ) {
          return (
            a.type === "package"
              ? -1
              : 1
          );
        }

        return a.name.localeCompare(
          b.name
        );

      });


      nodes.forEach(
        (node) => {
          sortTree(
            node.children
          );
        }
      );


      return nodes;
    }


    return sortTree(
      roots
    );

  }, [graphData]);


  // =====================================================
  // TREE EXPANSION
  // =====================================================

  function toggleNode(nodeId) {

    setExpandedNodes(
      (previous) => {

        const next =
          new Set(previous);


        if (
          next.has(nodeId)
        ) {
          next.delete(nodeId);
        } else {
          next.add(nodeId);
        }


        return next;

      }
    );

  }


  // =====================================================
  // SELECT NODE
  // =====================================================

  function selectNode(node) {
    setSelectedNode(node);
  }


  // =====================================================
  // TREE RENDERER
  // =====================================================

  function renderTree(
    nodes,
    depth = 0
  ) {

    return nodes.map(
      (node) => {

        const hasChildren =
          node.children.length > 0;


        const isExpanded =
          expandedNodes.has(
            node.id
          );


        const isSelected =
          selectedNode?.id ===
          node.id;


        return (
          <div
            key={node.id}
          >

            <div
              className={
                isSelected
                  ? "tree-item selected"
                  : "tree-item"
              }

              style={{
                paddingLeft:
                  `${16 + depth * 20}px`,
              }}

              onClick={() => {

                selectNode(node);


                if (hasChildren) {
                  toggleNode(
                    node.id
                  );
                }

              }}
            >

              {hasChildren ? (

                <span className="tree-chevron">
                  {isExpanded
                    ? "\u2304"
                    : "\u203A"}
                </span>

              ) : (

                <span className="tree-spacer" />

              )}


              <span
                className={
                  `tree-icon ${node.type}`
                }
              >
                {node.type ===
                "package"
                  ? "\u25B0"
                  : "\u25A1"}
              </span>


              <span className="tree-name">
                {node.name}
              </span>

            </div>


            {hasChildren &&
              isExpanded &&
              renderTree(
                node.children,
                depth + 1
              )}

          </div>
        );

      }
    );

  }


  // =====================================================
  // REPOSITORY COUNTS
  // =====================================================

  const counts = {

    packages:
      graphData.nodes.filter(
        (node) =>
          node.type ===
          "package"
      ).length,

    files:
      graphData.nodes.filter(
        (node) =>
          node.type ===
          "file"
      ).length,

    classes:
      graphData.nodes.filter(
        (node) =>
          node.type ===
          "class"
      ).length,

    functions:
      graphData.nodes.filter(
        (node) =>
          node.type ===
          "function"
      ).length,

  };


  // =====================================================
  // NODE LOOKUP
  // =====================================================

  const nodeLookup =
    useMemo(() => {

      return new Map(
        graphData.nodes.map(
          (node) => [
            node.id,
            node,
          ]
        )
      );

    }, [graphData]);


  // =====================================================
  // SELECTED NODE RELATIONSHIPS
  // =====================================================

  const selectedStats =
    useMemo(() => {

      if (
        !selectedNode
      ) {
        return {
          imports: [],
          dependents: [],
          children: [],
        };
      }


      const nodeId =
        selectedNode.id;


      const imports =
        graphData.edges.filter(
          (edge) =>
            edge.source ===
              nodeId &&
            edge.type ===
              "imports"
        );


      const dependents =
        graphData.edges.filter(
          (edge) =>
            edge.target ===
              nodeId &&
            edge.type ===
              "imports"
        );


      const children =
        graphData.edges.filter(
          (edge) =>
            edge.source ===
              nodeId &&
            edge.type ===
              "contains"
        );


      return {
        imports,
        dependents,
        children,
      };

    }, [
      selectedNode,
      graphData,
    ]);


  // =====================================================
  // CLEAN DEPENDENCY GRAPH
  // =====================================================

  const dependencyGraph =
    useMemo(() => {

      if (
        !selectedNode ||
        selectedNode.type !==
          "file"
      ) {
        return {
          nodes: [],
          edges: [],
        };
      }


      const centerId =
        selectedNode.id;


      // -----------------------------------------------
      // DIRECT IMPORTS
      // -----------------------------------------------

      const importNodes =
        selectedStats.imports
          .map(
            (edge) =>
              nodeLookup.get(
                edge.target
              )
          )
          .filter(Boolean);


      // -----------------------------------------------
      // DIRECT DEPENDENTS
      // -----------------------------------------------

      const dependentNodes =
        selectedStats.dependents
          .map(
            (edge) =>
              nodeLookup.get(
                edge.source
              )
          )
          .filter(Boolean);


      const nodes = [];


      // -----------------------------------------------
      // IMPORTS - LEFT
      // -----------------------------------------------

      importNodes.forEach(
        (node, index) => {

          nodes.push({

            id: node.id,

            position: {
              x: 40,

              y:
                (index -
                  (importNodes.length -
                    1) /
                    2) *
                75,
            },

            data: {
              label:
                node.name,

              type:
                "import",
            },

            className:
              "dependency-node import-node",

          });

        }
      );


      // -----------------------------------------------
      // SELECTED FILE - CENTER
      // -----------------------------------------------

      nodes.push({

        id: centerId,

        position: {
          x: 360,
          y: 0,
        },

        data: {
          label:
            selectedNode.name,

          type:
            "selected",
        },

        className:
          "dependency-node selected",

      });


      // -----------------------------------------------
      // DEPENDENTS - RIGHT
      // -----------------------------------------------

      dependentNodes.forEach(
        (node, index) => {

          nodes.push({

            id: node.id,

            position: {
              x: 680,

              y:
                (index -
                  (dependentNodes.length -
                    1) /
                    2) *
                75,
            },

            data: {
              label:
                node.name,

              type:
                "dependent",
            },

            className:
              "dependency-node dependent-node",

          });

        }
      );


      // -----------------------------------------------
      // EDGES
      // -----------------------------------------------

      const edges = [];


      // Selected file -> imported files

      selectedStats.imports.forEach(
        (edge, index) => {

          edges.push({

            id:
              `import-${index}`,

            source:
              centerId,

            target:
              edge.target,

            type:
              "smoothstep",

          });

        }
      );


      // Dependent files -> selected file

      selectedStats.dependents.forEach(
        (edge, index) => {

          edges.push({

            id:
              `dependent-${index}`,

            source:
              edge.source,

            target:
              centerId,

            type:
              "smoothstep",

          });

        }
      );


      return {
        nodes,
        edges,
      };

    }, [
      selectedNode,
      selectedStats,
      nodeLookup,
    ]);


  // =====================================================
  // DEPENDENCY NODE CLICK
  // =====================================================

  function handleDependencyClick(
    event,
    node
  ) {

    const target =
      nodeLookup.get(
        node.id
      );


    if (target) {
      setSelectedNode(
        target
      );
    }

  }


  // =====================================================
  // UI
  // =====================================================

  return (
    <div className="app">


      {/* =================================================
          TOP BAR
          ================================================= */}

      <header className="topbar">

        <div className="brand">

          <h1>
            CodeSense
          </h1>

          <p>
            Codebase intelligence
          </p>

        </div>


        <div className="repo-controls">

          <input
            type="text"
            placeholder="GitHub repository URL"
            value={repoUrl}
            onChange={(event) =>
              setRepoUrl(
                event.target.value
              )
            }
          />


          <button
            className="analyze-button"
            onClick={
              analyzeRepository
            }
            disabled={loading}
          >
            {loading
              ? "Analyzing..."
              : "Analyze Repository"}
          </button>

        </div>

      </header>


      {/* =================================================
          WORKSPACE
          ================================================= */}

      <main className="workspace">

        <section className="explorer-panel">


          {/* =================================================
              PANEL HEADER
              ================================================= */}

          <div className="panel-header">

            <div>

              <h2>
                Architecture Explorer
              </h2>

              <p>
                Explore the structure
                and relationships
                inside the repository.
              </p>

            </div>

          </div>


          {/* =================================================
              STATS
              ================================================= */}

          <div className="stats-bar">

            <div className="stat">

              <strong>
                {counts.packages}
              </strong>

              <span>
                Packages
              </span>

            </div>


            <div className="stat">

              <strong>
                {counts.files}
              </strong>

              <span>
                Files
              </span>

            </div>


            <div className="stat">

              <strong>
                {counts.classes}
              </strong>

              <span>
                Classes
              </span>

            </div>


            <div className="stat">

              <strong>
                {counts.functions}
              </strong>

              <span>
                Functions
              </span>

            </div>

          </div>


          {/* =================================================
              ERROR
              ================================================= */}

          {error && (

            <div className="error-message">
              {error}
            </div>

          )}


          {/* =================================================
              CONTENT
              ================================================= */}

          <div className="explorer-content">


            {/* =================================================
                REPOSITORY TREE
                ================================================= */}

            <aside className="repository-tree">

              <div className="tree-header">

                <span>
                  REPOSITORY
                </span>

                <span>
                  {counts.files} files
                </span>

              </div>


              <div className="tree-content">

                {architecture.length ===
                0 ? (

                  <div className="tree-empty">

                    <div>
                      {"\u25C7"}
                    </div>

                    <p>
                      Analyze a repository
                      to explore its
                      architecture.
                    </p>

                  </div>

                ) : (

                  renderTree(
                    architecture
                  )

                )}

              </div>

            </aside>


            {/* =================================================
                RIGHT PANEL
                ================================================= */}

            <section className="overview-panel">


              {!selectedNode ? (

                <div className="overview-empty">

                  <div className="overview-icon">
                    {"\u25C7"}
                  </div>

                  <h3>
                    Repository Overview
                  </h3>

                  <p>
                    Select a package or
                    file from the explorer
                    to inspect it.
                  </p>

                </div>

              ) : (

                <div className="selected-node-view">


                  {/* =================================================
                      SELECTED NODE HEADER
                      ================================================= */}

                  <div className="selected-header">

                    <div>

                      <span
                        className={
                          `node-type-badge ${selectedNode.type}`
                        }
                      >
                        {selectedNode.type}
                      </span>

                      <h2>
                        {
                          selectedNode.name
                        }
                      </h2>

                    </div>

                  </div>


                  {/* =================================================
                      FILE / PACKAGE STATS
                      ================================================= */}

                  <div className="info-grid">


                    <div className="info-card">

                      <span>
                        Node ID
                      </span>

                      <code>
                        {
                          selectedNode.id
                        }
                      </code>

                    </div>


                    {selectedNode.type ===
                      "file" && (

                      <>

                        <div className="info-card">

                          <span>
                            Imports
                          </span>

                          <strong>
                            {
                              selectedStats
                                .imports
                                .length
                            }
                          </strong>

                        </div>


                        <div className="info-card">

                          <span>
                            Dependents
                          </span>

                          <strong>
                            {
                              selectedStats
                                .dependents
                                .length
                            }
                          </strong>

                        </div>

                      </>

                    )}


                    {selectedNode.type ===
                      "package" && (

                      <div className="info-card">

                        <span>
                          Contents
                        </span>

                        <strong>
                          {
                            selectedStats
                              .children
                              .length
                          }
                        </strong>

                      </div>

                    )}

                  </div>


                  {/* =================================================
                      DEPENDENCY INTELLIGENCE
                      ================================================= */}

                  {selectedNode.type ===
                    "file" && (

                    <div className="dependency-section">


                      {/* HEADER */}

                      <div className="dependency-header">

                        <div>

                          <span>
                            RELATIONSHIPS
                          </span>

                          <h3>
                            Dependency Map
                          </h3>

                        </div>


                        <div className="dependency-legend">

                          <span>

                            <i className="legend-dot selected" />

                            Selected

                          </span>


                          <span>

                            <i className="legend-dot import" />

                            Imports

                          </span>


                          <span>

                            <i className="legend-dot dependent" />

                            Dependents

                          </span>

                        </div>

                      </div>


                      {/* GRAPH */}

                      <div className="dependency-graph">

                        {dependencyGraph.nodes.length ===
                        0 ? (

                          <div className="graph-empty">

                            No dependency
                            relationships found.

                          </div>

                        ) : (

                          <ReactFlow

                            nodes={
                              dependencyGraph.nodes
                            }

                            edges={
                              dependencyGraph.edges
                            }

                            fitView

                            fitViewOptions={{
                              padding:
                                0.25,
                            }}

                            nodesConnectable={
                              false
                            }

                            nodesDraggable={
                              true
                            }

                            onNodeClick={
                              handleDependencyClick
                            }

                            minZoom={
                              0.3
                            }

                            maxZoom={
                              1.8
                            }

                          >

                            <Background />

                            <Controls />

                          </ReactFlow>

                        )}

                      </div>


                      {/* =================================================
                          RELATIONSHIP LISTS
                          ================================================= */}

                      <div className="relationship-grid">


                        {/* IMPORTS */}

                        <div className="relationship-card">

                          <div className="relationship-title">

                            <span className="relationship-dot import" />

                            Imports

                            <strong>
                              {
                                selectedStats
                                  .imports
                                  .length
                              }
                            </strong>

                          </div>


                          <div className="relationship-list">

                            {selectedStats.imports.length ===
                            0 ? (

                              <span className="empty-text">
                                No internal
                                imports.
                              </span>

                            ) : (

                              selectedStats
                                .imports
                                .map(
                                  (
                                    edge
                                  ) => {

                                    const node =
                                      nodeLookup.get(
                                        edge.target
                                      );


                                    if (!node) {
                                      return null;
                                    }


                                    return (

                                      <button
                                        key={
                                          edge.target
                                        }

                                        className="relationship-item"

                                        onClick={() =>
                                          setSelectedNode(
                                            node
                                          )
                                        }
                                      >

                                        {node.name}

                                      </button>

                                    );

                                  }
                                )

                            )}

                          </div>

                        </div>


                        {/* DEPENDENTS */}

                        <div className="relationship-card">

                          <div className="relationship-title">

                            <span className="relationship-dot dependent" />

                            Dependents

                            <strong>
                              {
                                selectedStats
                                  .dependents
                                  .length
                              }
                            </strong>

                          </div>


                          <div className="relationship-list">

                            {selectedStats.dependents.length ===
                            0 ? (

                              <span className="empty-text">
                                No internal
                                dependents.
                              </span>

                            ) : (

                              selectedStats
                                .dependents
                                .map(
                                  (
                                    edge
                                  ) => {

                                    const node =
                                      nodeLookup.get(
                                        edge.source
                                      );


                                    if (!node) {
                                      return null;
                                    }


                                    return (

                                      <button
                                        key={
                                          edge.source
                                        }

                                        className="relationship-item"

                                        onClick={() =>
                                          setSelectedNode(
                                            node
                                          )
                                        }
                                      >

                                        {node.name}

                                      </button>

                                    );

                                  }
                                )

                            )}

                          </div>

                        </div>

                      </div>

                    </div>

                  )}


                  {/* =================================================
                      PACKAGE INFO
                      ================================================= */}

                  {selectedNode.type ===
                    "package" && (

                    <div className="coming-section">

                      <span>
                        PACKAGE
                      </span>

                      <h3>
                        Package Contents
                      </h3>

                      <p>
                        Expand this package
                        in the repository
                        explorer to inspect
                        its files.
                      </p>

                    </div>

                  )}

                </div>

              )}

            </section>

          </div>

        </section>

        {/* =====================================================
            AI CODEBASE Q&A
            ===================================================== */}
        <section
          className="qa-panel"
          style={{
            margin: "24px 0",
            padding: "24px",
            border: "1px solid var(--border-color, #2b3445)",
            borderRadius: "16px",
            background: "var(--panel-bg, #111827)",
            color: "var(--text-primary, #e5e7eb)",
          }}
        >
          <div className="qa-heading" style={{ marginBottom: "18px" }}>
            <span
              style={{
                color: "var(--accent-color, #7c9cff)",
                fontSize: "11px",
                fontWeight: 700,
                letterSpacing: "1.5px",
              }}
            >
              CODEBASE INTELLIGENCE
            </span>
            <h2 className="qa-title" style={{ margin: "8px 0", fontSize: "22px" }}>
              Ask your codebase
            </h2>
            <p className="qa-description" style={{ margin: 0, opacity: 0.75, lineHeight: 1.6 }}>
              Ask how the repository works and get an answer with source evidence.
              Use the GitHub URL entered above.
            </p>
          </div>

          <form
            className="qa-form"
            onSubmit={(event) => {
              event.preventDefault();
              askRepository();
            }}
            style={{ display: "grid", gap: "12px" }}
          >
            <textarea
              className="qa-question-input"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder="Example: Which function clones the repository, and how does it work?"
              rows={3}
              maxLength={2000}
              aria-label="Question about the repository"
              style={{
                width: "100%",
                boxSizing: "border-box",
                resize: "vertical",
                padding: "14px",
                borderRadius: "10px",
                border: "1px solid var(--border-color, #374151)",
                background: "var(--input-bg, #0b1220)",
                color: "inherit",
                font: "inherit",
                lineHeight: 1.5,
              }}
            />
            <div style={{ display: "flex", alignItems: "center", gap: "12px", flexWrap: "wrap" }}>
              <button
                type="submit"
                disabled={qaLoading}
                className="analyze-button"
                style={{ padding: "11px 18px", cursor: qaLoading ? "wait" : "pointer" }}
              >
                {qaLoading ? "Analyzing codebase..." : "Ask CodeSense"}
              </button>
              {qaLoading && (
                <span style={{ fontSize: "13px", opacity: 0.75 }}>
                  Cloning, indexing, and searching repository code. This may take a little while.
                </span>
              )}
            </div>
          </form>

          {qaError && (
            <div
              role="alert"
              className="error-message"
              style={{ marginTop: "16px" }}
            >
              {qaError}
            </div>
          )}

          {qaResult && (
            <div className="qa-results" style={{ marginTop: "24px" }}>
              <h3 className="qa-section-title" style={{ marginBottom: "10px" }}>Answer</h3>
              <div
                className="qa-answer"
                style={{
                  padding: "16px",
                  borderRadius: "10px",
                  background: "var(--answer-bg, #0b1220)",
                  border: "1px solid var(--border-color, #2b3445)",
                  lineHeight: 1.7,
                  whiteSpace: "pre-wrap",
                  overflowWrap: "anywhere",
                }}
              >
              <ReactMarkdown
  remarkPlugins={[remarkGfm]}
  components={{
    h1: ({ children }) => <h1 className="qa-md-h1">{children}</h1>,
    h2: ({ children }) => <h2 className="qa-md-h2">{children}</h2>,
    h3: ({ children }) => <h3 className="qa-md-h3">{children}</h3>,
    p: ({ children }) => <p className="qa-md-p">{children}</p>,
    ul: ({ children }) => <ul className="qa-md-list">{children}</ul>,
    ol: ({ children }) => <ol className="qa-md-list">{children}</ol>,
    li: ({ children }) => <li>{children}</li>,
    strong: ({ children }) => <strong>{children}</strong>,
    code: ({ children, className }) => {
      const isBlock = /language-/.test(className || "");

      return isBlock ? (
        <code className={className}>{children}</code>
      ) : (
        <code className="qa-inline-code">{children}</code>
      );
    },
    pre: ({ children }) => (
      <pre className="qa-code-block">{children}</pre>
    ),
  }}
>
  {qaResult.answer || "No answer was returned."}
</ReactMarkdown>
              </div>

              <h3 className="qa-section-title" style={{ margin: "22px 0 10px" }}>Source evidence</h3>
              {Array.isArray(qaResult.sources) && qaResult.sources.length > 0 ? (
                <div className="qa-sources" style={{ display: "grid", gap: "10px" }}>
                  {qaResult.sources.map((source, index) => (
                    <article
                      className="qa-source-card"
                      key={`${source.file || "source"}-${source.start_line || 0}-${index}`}
                      style={{
                        display: "grid",
                        gap: "6px",
                        padding: "14px",
                        borderRadius: "10px",
                        border: "1px solid var(--border-color, #2b3445)",
                        background: "var(--source-bg, #151e2e)",
                      }}
                    >
                      <strong className="qa-source-file" style={{ overflowWrap: "anywhere" }}>
                        {source.file || "Unknown file"}
                      </strong>
                      <span className="qa-source-lines" style={{ fontSize: "13px", opacity: 0.8 }}>
                        Lines {source.start_line ?? "?"}–{source.end_line ?? "?"}
                      </span>
                      {Number.isFinite(Number(source.score)) && (
                        <span className="qa-source-score" style={{ fontSize: "12px", opacity: 0.7 }}>
                          Retrieval score: {Number(source.score).toFixed(3)}
                        </span>
                      )}
                    </article>
                  ))}
                </div>
              ) : (
                <p style={{ opacity: 0.75 }}>No source references were returned for this answer.</p>
              )}

              {qaResult.index_stats && (
                <p className="qa-index-stats" style={{ marginTop: "16px", fontSize: "12px", opacity: 0.65 }}>
                  Indexed {qaResult.index_stats.chunks_created ?? "?"} code chunks from {qaResult.index_stats.files_read ?? "?"} files.
                </p>
              )}
            </div>
          )}
        </section>

      </main>

    </div>
  );
}


export default App;