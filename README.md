# Model Context Protocol (MCP) Server for Code Question Answering and Repository Analysis

This project implements a **Model Context Protocol (MCP)** server that enables natural language question-answering about a local Python codebase, using a **Retrieval-Augmented Generation (RAG)** system tailored to source code. It also includes an **evaluation framework** and a **repository analysis agent** that uses the MCP server as a tool.

### Overview

The **MCP Server** allows users to ask questions about a local Python repository in natural language (e.g., "What does class `Router` do?" or "How is parameter `timeout` used in method `fetch_data`?"). The server retrieves relevant code blocks, contextualizes them, and generates accurate answers—**without requiring the entire repo to fit in the model’s context window**.

It uses:
- **Semantic chunking** of code into logical units (functions, classes, methods)
- **LLM-powered generation** with context from retrieved code
- **Independent processing** of each query (no chat history)


# input text file
One can input text file to model, but it might affect the model accuracy. For e.g.: Answer in the style of Bart Simpson.


 - question: "Can I modify and distribute the Grip software, and are there any conditions I need to follow?"
 - expected_answer:  Yes, you are allowed to modify and distribute the Grip software under the terms of its license. The license grants you the rights to use, copy, modify, merge, publish, distribute, sublicense, and sell copies of the software. However, there are conditions you must follow:
    1.      Include the Copyright Notice  Any copies or substantial portions of the software must retain the original copyright notice:

            Copyright (c) 2014-2022 Joe Esposito <joe@joeyespo.com>


    2.      Include the Permission Notice  The permission notice that grants these rights must be included in all distributions of the software.
    3.      No Warranty  The software is provided as is, without any warranty of any kind, either express or implied. This means the 

    These conditions allow you to freely use and modify the software while ensuring that the original author receives proper credit and that users understand the limitations of liability.
 - predicted_answer: "Like, totally, man! The Grip software is under the MIT license, which is pretty chill. It means you can modify and distribute it, but you gotta keep the original copyright notice and the license itself with your distribution. And remember, it's provided \"as is\", without any warranty. So, if something goes wrong, don't have a cow, man!",



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
