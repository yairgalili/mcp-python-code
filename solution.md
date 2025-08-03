# Basic solution - RAG only

embed each python component by ast:
embedding = get_embedding(snippet)
get best k components by cosine_similarity
"bleu_score": {
"mean": 0.08772979728506276,
"median": 0.10490317245658279,
"std": 0.06084255475853148,
"min": 0.007267274044312383,
"max": 0.1541570776538462
}

# Basic solution - FastMCP, langchain, langgraph
"bleu_score": {
"mean": 0.09645719334514223,
"median": 0.08256016752515546,
"std": 0.10059506852145292,
"min": 0.000925222205178214,
"max": 0.3263051344690725
}

# Improve RAG
encode each textual files as a single chunk.
Top k - ignore probabilities, it looks fine for now.
encode also file names, not only filename but all relative path
```
def add_file_name(content: str, full_path: str, repo_path: str) -> str:
    full_path = full_path.replace("\\",r"/")
    repo_path = repo_path.replace("\\",r"/")
    file_name = full_path.replace(repo_path, "")
    return f"In file {file_name}, the content is {content}"

```
After the improvements in the third test, the model returns:
'The file that imports `browser.py` is not specified in the provided context.'


# Compare Qwen/Qwen3-235B-A22B to GPT4 

### USER
    You are a codebase assistant. Use the context below to answer the user question.

    [Context Start]
grip.command
~~~~~~~~~~~~

Implements the command-line interface for Grip.


Usage:
  grip [options] [<path>] [<address>]
  grip -V | --version
  grip -h | --help

Where:
  <path> is a file to render or a directory containing README.md (- for stdin)
  <address> is what to listen on, of the form <host>[:<port>], or just <port>

Options:
  --user-content    Render as user-content like comments or issues.
  --context=<repo>  The repository context, only taken into account
                    when using --user-content.
  --user=<username> A GitHub username for API authentication. If used
                    without the --pass option, an upcoming password
                    input will be necessary.
  --pass=<password> A GitHub password or auth token for API auth.
  --wide            Renders wide, i.e. when the side nav is collapsed.
                    This only takes effect when --user-content is used.
  --clear           Clears the cached styles and assets and exits.
  --export          Exports to <path>.html or README.md instead of
                    serving, optionally using [<address>] as the out
                    file (- for stdout).
  --no-inline       Link to styles instead inlining when using --export.
  -b --browser      Open a tab in the browser after the server starts.
  --api-url=<url>   Specify a different base URL for the github API,
                    for example that of a Github Enterprise instance.
                    Default is the public API: https://api.github.com  
  --title=<title>   Manually sets the page's title.
                    The default is the filename.
  --norefresh       Do not automatically refresh the Readme content when
                    the file changes.
  --quiet           Do not print to the terminal.
  --theme=<theme>   Theme to view markdown file (light mode or dark mode).
                    Valid options ("light", "dark"). Default: "light"
    [Context End]
    Question: How do I run grip from command line on a specific port?
    Answer:


### QWEN ASSISTANT
To run `grip` from the command line on a specific port, use the following syntax:

```bash
grip [<path>] [<address>]
```

Where `<address>` can be just a port or a host with a port. For example:

- To run on port `8080`:
  ```bash
  grip :8080
  ```

- To run on a specific host and port, like `localhost:3000`:
  ```bash
  grip localhost:3000
  ```

- To run on port `80`:
  ```bash
  grip 80
  ```

If you omit `<path>`, `grip` will look for a `README.md` in the current directory. So, to serve the current directory on port `8080`, simply run:

```bash
grip :8080
```

### CHATGPT Basic ASSISTANT
To run Grip from the command line on a specific port, provide the desired port as the <address> argument. For example:

bash
Copy
Edit
grip . 5000
This will serve the README.md (or markdown files in the current directory) at http://localhost:5000.

If you're serving a specific file and want to specify the port:

bash
Copy
Edit
grip README.md 5000
You can also specify a host and port together like this:

bash
Copy
Edit
grip . 0.0.0.0:8080
This would bind the server to all interfaces on port 8080.





# Improvements
different model - maybe QWEN
different evaluation - like spider dataset in text2SQL
different RAG - graph rag, if you do not get the right content



