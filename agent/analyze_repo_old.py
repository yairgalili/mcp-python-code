# agent.py
import os
import asyncio
from fastmcp import Client
from langchain import hub
from langchain_community.llms import OpenAI
from langchain.agents import AgentExecutor, create_react_agent

prompt = hub.pull("hwchase17/react")
model = OpenAI(model="gpt-4o")


async def get_agent(mcp_url="http://localhost:8080/mcp"):
    async with Client(mcp_url) as client:
        # async with Client(mcp) as client:
        # Get tools from the MCP client
        tools = await client.list_tools()
        # Create the agent
        agent = create_react_agent(model, tools, prompt)
        return AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)

async def analyze_repo(repo_path):
    agent_executor = await get_agent()
    query = f"What is the general architecture of this repo {repo_path}?, List all major classes and their purposes. What external libraries or frameworks does this repo use?, Are there any design patterns used in this repo?, What are the main services and how do they interact?"
    response = agent_executor.invoke({"input": query})
    
    with open("report.md", "w") as f:
        f.write(response["output"])
    print("Report written to report.md")

if __name__ == "__main__":
    asyncio.run(analyze_repo("./grip-repo"))
