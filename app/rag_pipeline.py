# --- app/rag_pipeline.py ---
import os
from app.index_builder import get_chunks_for_repo
from app.utils import get_top_k_chunks, call_openai_with_context

# In-memory index (could use Chroma or FAISS for persistent index)
repo_index_cache = {}

# Main entrypoint for question-answering
def answer_question(repo_path: str, question: str) -> str:
    if repo_path not in repo_index_cache:
        repo_index_cache[repo_path] = get_chunks_for_repo(repo_path)

    chunks = repo_index_cache[repo_path]
    top_chunks = get_top_k_chunks(question, chunks, k=5)
    context = "\n\n".join([chunk['content'] for chunk in top_chunks])
    return call_openai_with_context(question, context)

