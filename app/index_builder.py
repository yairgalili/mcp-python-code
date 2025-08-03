# --- app/index_builder.py ---
import os
import ast
import re
from tqdm import tqdm
from app.utils import get_embedding
from binaryornot.check import is_binary

def add_file_name(content: str, full_path: str, repo_path: str) -> str:
    full_path = full_path.replace("\\",r"/")
    repo_path = repo_path.replace("\\",r"/")
    file_name = full_path.replace(repo_path + "/", "")
    return f"In file {file_name}, the content is {content}"

# Parse all .py files and extract class/function chunks
def get_chunks_for_repo(repo_path: str):
    chunks = []
    for dirpath, _, filenames in os.walk(repo_path):
        for file in tqdm(filenames, desc="Processing files"):
            full_path = os.path.join(dirpath, file)
            if is_binary(full_path):
                continue
            try:
                if file.endswith(".py"):
                    with open(full_path, "r", encoding="utf-8") as f:
                        source = f.read()
                        tree = ast.parse(source)
                        for node in tqdm(ast.walk(tree), desc="Processing nodes"):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                start_line = node.lineno - 1
                                end_line = getattr(node, "end_lineno", None) or start_line + 1
                                snippet = "\n".join(source.splitlines()[start_line:end_line])
                                snippet = add_file_name(snippet, full_path, repo_path)
                                embedding = get_embedding(snippet)
                                chunks.append({"content": snippet, "embedding": embedding})

                            elif isinstance(node, ast.Module):
                                for element in node.body:
                                    start_line = element.lineno - 1
                                    end_line = getattr(element, "end_lineno", None) or start_line + 1
                                    snippet = "\n".join(source.splitlines()[start_line:end_line])
                                    snippet = add_file_name(snippet, full_path, repo_path)
                                    embedding = get_embedding(snippet)
                                    chunks.append({"content": snippet, "embedding": embedding})
                                    # ast.Expr, ast.Import, ast.ImportFrom, ast.Constant, ast.alias, ast.arguments, ast.With, ast.Call

                else:
                    with open(full_path, "r", encoding="utf-8") as f:
                        source = f.read()
                        source = add_file_name(source, full_path, repo_path)
                        embedding = get_embedding(source)
                        chunks.append({"content": source, "embedding": embedding})

            except Exception as e:
                print(f"Error processing {full_path}: {e}")
                continue

    return chunks

