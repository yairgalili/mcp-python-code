# client.py
import asyncio
import os
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langchain_community.llms import OpenAI


# Set up your model (e.g., GPT-4o via OpenAI)
model = OpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# Define server parameters (update path/env as needed)
server_params = StdioServerParameters(
    command="python",
    args=["server.py"],
    env={"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
)

async def run_single_agent(repo_path="./grip-repo"):
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print("✅ MCP session initialized.")

                # Load tools from MCP server
                tools = await load_mcp_tools(session)
                print(f"🔧 Loaded tools: {[tool.name for tool in tools]}")

                # Create LangChain ReAct agent
                agent = create_react_agent(model=model, tools=tools)

                # 🔹 Specific prompt to run (set this as needed)
                query = f"What is the general architecture of this repo {repo_path}?, List all major classes and their purposes. What external libraries or frameworks does this repo use?, Are there any design patterns used in this repo?, What are the main services and how do they interact?"

                print(f"\n🚀 Running agent with prompt: '{query}'")

                try:
                    result = await agent.ainvoke({"messages": [{"role": "user", "content": query}]})
                    output = result.get("output", "No output found.")
                    print(f"\n🤖 Response: {output}")
                except Exception as e:
                    print(f"❌ Error during agent invocation: {e}")

    except Exception as e:
        print(f"🚨 Error initializing agent or session: {e}")


if __name__ == "__main__":
    asyncio.run(run_single_agent())