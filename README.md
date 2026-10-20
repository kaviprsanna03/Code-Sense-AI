# CodeSense AI

**Understand any codebase. Trace its architecture. Ask questions grounded in source code.**

CodeSense AI is an AI-powered codebase intelligence workspace that helps developers explore unfamiliar repositories, understand code dependencies, and ask questions about implementation details using natural language.

Instead of manually jumping between files, developers can explore repository structure and receive AI-generated explanations supported by relevant source files and line references.

## Overview

Understanding an unfamiliar codebase can be time-consuming. Developers need to locate files, trace dependencies, understand functions, and connect individual components to the larger system.

CodeSense AI brings these workflows into one interface by combining static code analysis, dependency visualization, semantic retrieval, and large language model (LLM) generation.

## Features

- **Architecture Explorer** — Explore repository structure and visualize relationships between code components.
- **Multi-language parsing** — Analyze Python, JavaScript, JSX, TypeScript, and TSX source files.
- **Codebase statistics** — Inspect files, classes, functions, and other extracted repository information.
- **Natural-language Q&A** — Ask questions about repository implementation and receive AI-generated explanations.
- **Retrieval-augmented generation (RAG)** — Retrieve relevant source-code chunks to provide context for answers.
- **Source evidence** — View relevant file paths, line ranges, and retrieval scores alongside answers.
- **Markdown rendering** — Read formatted explanations, lists, inline code, and code blocks in the workspace.

## Architecture

CodeSense AI combines a React frontend with a Python backend and a retrieval pipeline.

```text
                 Repository URL
                       |
                       v
              Repository Cloning
                       |
                       v
              Source File Discovery
                       |
                       v
              Tree-sitter Parsing
                       |
             +---------+---------+
             |                   |
             v                   v
       Code Analysis       Dependency Graph
             |                   |
             +---------+---------+
                       |
                       v
                Architecture UI


                  User Question
                       |
                       v
              Semantic Retrieval
                       |
                       v
              Relevant Code Chunks
                       |
                       v
                 Groq LLM
                       |
                       v
             Answer + Source Evidence
```

### Technology stack

| Component | Technology |
|---|---|
| Frontend | React, Vite |
| Backend API | Python, FastAPI |
| Source parsing | Tree-sitter |
| Semantic retrieval | Sentence Transformers, FAISS |
| Answer generation | Groq API |
| Repository operations | Git |
| UI styling | CSS |

## Getting started

### Prerequisites

Install the following before running the project:

- Git
- Python 3.13 or a compatible Python version for the dependencies
- Node.js and npm
- A Groq API key for LLM-powered answers

The first semantic-indexing run may download embedding-model files from Hugging Face, so internet access is required.

### 1. Clone the repository

```bash
git clone https://github.com/kaviprsanna03/Code-Sense-AI.git
cd Code-Sense-AI
```

### 2. Set up the backend

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt
```

Configure your Groq API key using the environment variable `GROQ_API_KEY`. For local development, you can place it in a `.env` file in the project root if the backend's environment configuration loads that file:

```dotenv
GROQ_API_KEY=your_groq_api_key
```

**Security:** Never commit your API key or `.env` file to Git.

Start the backend from the project root:

```bash
uvicorn app.main:app --reload --app-dir backend
```

The API should be available at:

- API base: `http://127.0.0.1:8000`
- Health check: `http://127.0.0.1:8000/health`

### 3. Set up the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually `http://localhost:5173`.

### 4. Use CodeSense AI

1. Enter a GitHub repository URL in the repository input.
2. Analyze the repository.
3. Explore its file structure, code statistics, and dependency relationships.
4. Open the codebase Q&A section.
5. Ask a question about a function, module, or implementation detail.
6. Review the generated answer and inspect its source evidence.

Example questions:

- Which function clones the repository, and how is the temporary workspace created?
- How are dependencies between source files represented?
- Which files implement the repository analysis pipeline?
- How does the application retrieve code relevant to a question?

Answers depend on the repository content successfully parsed and retrieved by the system.

## API endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Check backend health |
| `POST /analyze` | Analyze a repository |
| `POST /ask` | Ask a question about a repository |

For the exact request and response schemas, inspect the FastAPI application or open the interactive API documentation at `http://127.0.0.1:8000/docs` while the backend is running.

## Project structure

```text
Code-Sense-AI/
├── backend/
│   ├── app/
│   │   ├── rag/
│   │   │   ├── llm.py
│   │   │   └── qa.py
│   │   ├── analyzer.py
│   │   ├── graph.py
│   │   ├── main.py
│   │   ├── parser.py
│   │   └── repository.py
│   ├── requirements.txt
│   ├── test_llm.py
│   └── test_qa.py
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   └── App.css
│   ├── package.json
│   └── package-lock.json
├── .gitignore
└── README.md
```

## Verification

The following checks have been performed during development:

- Frontend production build completed successfully with Vite.
- Manual LLM generation check returned a response.
- Manual repository Q&A check cloned the repository, generated an answer, and returned source references.
- Git changes were committed and pushed to the `main` branch.

The manual checks are scripts rather than automated pytest test functions. Automated test coverage remains a future improvement.

## Current limitations

- Answer quality depends on source parsing, retrieval relevance, and LLM generation.
- Returned source evidence should be inspected to verify that claims are supported by the underlying implementation.
- Initial indexing can take time while repositories are cloned and embedding models are loaded.
- The production build currently reports a JavaScript bundle-size warning above 500 kB.
- Automated regression tests and broader repository-scale evaluation are still needed.

## Future improvements

Potential directions include:

- Automated tests for parsing, graph construction, retrieval, and API endpoints.
- Better retrieval evaluation and answer-grounding checks.
- Improved indexing performance for larger repositories.
- Incremental indexing when source files change.
- More efficient frontend bundle splitting.
- Expanded language coverage and richer code navigation.

## Contributing

Contributions, bug reports, and suggestions are welcome. For significant changes, open an issue to discuss the proposed improvement before submitting a pull request.

## License

## License

This project is licensed under the [MIT License](LICENSE).

You are free to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software, subject to the conditions of the MIT License.

See the [`LICENSE`](LICENSE) file for the full license text.