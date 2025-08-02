# --- app/index_builder.py ---
import os
import ast
from tqdm import tqdm
from app.utils import get_embedding

# Parse all .py files and extract class/function chunks
def get_chunks_for_repo(repo_path: str):
    chunks = []
    for dirpath, _, filenames in os.walk(repo_path):
        for file in tqdm(filenames, desc="Processing files"):
            if file.endswith(".py"):
                full_path = os.path.join(dirpath, file)
                with open(full_path, "r", encoding="utf-8") as f:
                    try:
                        source = f.read()
                        tree = ast.parse(source)
                        for node in tqdm(ast.walk(tree), desc="Processing nodes"):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                start_line = node.lineno - 1
                                end_line = getattr(node, "end_lineno", None) or start_line + 1
                                snippet = "\n".join(source.splitlines()[start_line:end_line])
                                embedding = get_embedding(snippet)
                                chunks.append({"content": snippet, "embedding": embedding})
                    except Exception as e:
                        print(f"Error processing {full_path}: {e}")
                        continue
    return chunks

