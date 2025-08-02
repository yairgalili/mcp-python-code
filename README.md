# Directory structure (included here in markdown comments for clarity)
# 
# mcp_code_qa/
# ├── app/
# │   ├── __init__.py
# │   ├── main.py                 # FastAPI app
# │   ├── rag_pipeline.py         # RAG logic (chunking, embedding, retrieval, generation)
# │   ├── index_builder.py        # Indexing codebase (functions/classes)
# │   ├── utils.py                # Helpers
# ├── agent/
# │   └── analyze_repo.py         # Generates architecture report
# ├── eval/
# │   ├── evaluate.py             # Evaluation script using grip_qa
# │   └── questions.json          # Optional: additional test questions
# ├── requirements.txt
# ├── README.md





# --- requirements.txt ---
fastapi
uvicorn
openai
numpy
requests

# --- README.md ---
# MCP Code Q&A System

## Setup
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY=your_openai_key_here
```

## Running the Server
```bash
uvicorn app.main:app --reload
```

## Index a repo & Ask Questions
```bash
curl -X POST "http://localhost:8000/ask" -H "Content-Type: application/json" -d '{"repo_path": "./myrepo", "question": "What does class X do?"}'
```

## Run the Evaluation
```bash
python eval/evaluate.py <path_to_grip_qa.json> <path_to_repo>
```

## Run the Agent
```bash
python agent/analyze_repo.py <path_to_repo>
```

This will produce a `report.md` containing a high-level summary of the repo.
