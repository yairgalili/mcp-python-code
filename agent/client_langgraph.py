import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI # Assuming you use OpenAI LLM
import os


async def run_agent(repo_path):
    # Initialize the MCP client, pointing to your server's transport and URL
    client = MultiServerMCPClient(
        {
            "my_tools": {
                "transport": "streamable_http", # Or "streamable_http" and URL for HTTP server
                "url": "http://localhost:8080/mcp", # If using HTTP transport
            }
        }
    )

    # Get the tools exposed by your MCP server
    tools = await client.get_tools()
    print(tools)

    # Create a LangGraph agent with the LLM and the MCP tools
    llm = ChatOpenAI(model="gpt-4", api_key=os.getenv("OPENAI_API_KEY"))
    agent = create_react_agent(llm, tools)

    # Invoke the agent
    response = await agent.ainvoke({"messages": f"What is the general architecture of this repo {repo_path}?, List all major classes and their purposes. What external libraries or frameworks does this repo use?, Are there any design patterns used in this repo?, What are the main services and how do they interact?"})
    print(response["messages"][-1].content)


if __name__ == "__main__":
    repo_path = "./grip-repo"

    asyncio.run(run_agent(repo_path))