from app.main import mcp


if __name__ == "__main__":
    print("Starting MCP Server on http://localhost:8080")
    mcp.run(transport="http", host="0.0.0.0", port=8080)


# {
#   "tool": "list_files",
#   "input": {
#     "repo_path": "/Users/alice/myproject"
#   }
# }

# def is_safe_path(repo_path, allowed_base):
#     """Check if repo_path is within allowed base directory"""
#     base = os.path.abspath(allowed_base)
#     requested = os.path.abspath(repo_path)
#     return os.path.commonpath([base]) == base and requested.startswith(base)