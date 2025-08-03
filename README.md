# MCP Code Q&A System

Your goal is to write a Model Context Protocol (MCP) server that answers questions about a local repo. 
As an example, you can take the grip repo.
Given the root path of a Python project, your API should take in questions in natural language and answer them as text (potentially with code snippets). The questions should be processed independently of each other (not as a chat). 

The questions might include things like:
⦁	What does class X do?
⦁	How is service Y implemented?
⦁	How does method X use parameter Y?


To implement this functionality, you should use a RAG system where you will define and implement the various aspects such as chunking of the code, storage, indexing and retrieval. You can use existing libraries for any part of the project, as long as you can explain your choices. Your chunks should reflect coherent logical blocks of code (e.g. functions, classes, …) and not just be character/token based.

Your code should support large repos that could not fit in a model’s context window.

You should implement a way to automatically measure the quality of your system. For that purpose, we provide a set of 10 question/answer pairs at grip_qa. 
These can be considered references to measure against (of course, it is not required for each answer to be strictly identical to the reference one in order to be correct). 

Your evaluation script should be able to run your implementation of the QA system on the set of questions, compare the answers to the reference one and provide a numeric score capturing the quality of the system’s answers. It’s up to you to define the details of the approach and metrics you use.

Finally, implement an agent that uses your MCP server as a tool (it can also have other tools) to analyze a full repo and produce a report describing the general architecture, external dependencies and main design patterns of the repo.

Your submission should contain the following:
1.	A functional MCP server for code Q&A along with instructions on how to set the server up
2.	An evaluation script and a report on the quality of the server
3.	An agent for repo analysis using the MCP server above, and instructions on how to run it

Write your program in any language and use any LLM available (e.g. OpenAI’s GPT-4.1, Anthropic’s Claude, Llama, …), whether through an API or locally.


# Solution
## Running the MCP Server
```
python server.py
```

## Run the Evaluation
This will produce a `evaluation_report.json` file.
```
python eval/evaluate.py ./grip_qa
```

## Run the Agent

This will produce a `report.md` containing a high-level summary of the repo.

```
python agent\client_langgraph.py
```
