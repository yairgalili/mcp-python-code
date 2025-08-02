# --- agent/analyze_repo.py ---
import requests
import os
import json

MCP_URL = "http://localhost:8000/ask"

def analyze_repo(repo_path):
    questions = [
        "What is the general architecture of this repo?",
        "List all major classes and their purposes.",
        "What external libraries or frameworks does this repo use?",
        "Are there any design patterns used in this repo?",
        "What are the main services and how do they interact?",
    ]
    report = "# Repo Analysis\n"
    for q in questions:
        response = requests.post(MCP_URL, json={"repo_path": repo_path, "question": q})
        answer = response.json().get("answer", "[Error: no answer]")
        report += f"\n## {q}\n{answer}\n"

    with open("report.md", "w") as f:
        f.write(report)
    print("Report written to report.md")

if __name__ == "__main__":
    analyze_repo("./grip-repo")
