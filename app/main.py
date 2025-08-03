# --- app/main.py ---
import os
from pydantic import BaseModel, Field
from app.rag_pipeline import answer_question
from fastmcp import FastMCP

mcp = FastMCP(name="DynamicRepoMCP")


# Define a Pydantic BaseModel for input data
class QARequest(BaseModel):
    repo_path: str = Field(description="The path to the repository that contains the files to answer the question")
    question: str = Field(description="The question to answer")

# Define a tool for the MCP server
@mcp.tool()
async def ask_question(request: QARequest):
    """
    Ask a question about the repository
    """
    answer = answer_question(request.repo_path, request.question)
    return {"question": request.question, "answer": answer}


@mcp.tool()
def list_files(repo_path: str):
    """
    List all files in the repository
    """
    if not os.path.exists(repo_path):
        return {"error": f"Repo path does not exist: {repo_path}"}
    files = []
    for root, _, filenames in os.walk(repo_path):
        for f in filenames:
            files.append(os.path.relpath(os.path.join(root, f), repo_path))
    return {"files": files}


@mcp.tool()
def read_file(repo_path: str, file_path: str):
    """
    Read a specific file from the repo
    """
    full_path = os.path.join(repo_path, file_path)
    if not os.path.exists(full_path):
        return {"error": f"File not found: {full_path}"}
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {"content": content}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool()
def search_in_repo(repo_path: str, query: str):
    """
    Search for a keyword in all files of the repo
    """
    matches = []
    for root, _, filenames in os.walk(repo_path):
        for f in filenames:
            file_path = os.path.join(root, f)
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as fp:
                    for i, line in enumerate(fp.readlines()):
                        if query in line:
                            matches.append({
                                "file": os.path.relpath(file_path, repo_path),
                                "line": i + 1,
                                "content": line.strip()
                            })
            except Exception:
                continue
    return {"matches": matches}