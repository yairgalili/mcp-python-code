# Model Context Protocol (MCP) Server for Code Question Answering and Repository Analysis

This project implements a **Model Context Protocol (MCP)** server that enables natural language question-answering about a local Python codebase, using a **Retrieval-Augmented Generation (RAG)** system tailored to source code. It also includes an **evaluation framework** and a **repository analysis agent** that uses the MCP server as a tool.

### Overview

The **MCP Server** allows users to ask questions about a local Python repository in natural language (e.g., "What does class `Router` do?" or "How is parameter `timeout` used in method `fetch_data`?"). The server retrieves relevant code blocks, contextualizes them, and generates accurate answers—**without requiring the entire repo to fit in the model’s context window**.

It uses:
- **Semantic chunking** of code into logical units (functions, classes, methods)
- **LLM-powered generation** with context from retrieved code
- **Independent processing** of each query (no chat history)
  אני 
## Running the MCP Server
```
python server.py
```

## Run the Evaluation
This will produce a `evaluation_report.json` file.
```
python eval/evaluate.py ./grip-qa
```

## Run the Agent

This will produce a `report.md` containing a high-level summary of the repo.

```
python agent\client_langgraph.py
```
