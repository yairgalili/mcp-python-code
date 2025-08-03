import asyncio
from fastmcp import Client
from mcp import types
import requests
import json

from app.main import mcp

def test_fastmcp_server():
   base_url = "http://localhost:8080/sse"
   headers = {
       'accept': 'application/json, text/event-stream',
       'content-type': 'application/json'
   }
   
   print("check 1")
   
   init_payload = {
       "jsonrpc": "2.0",
       "method": "initialize",
       "params": {
           "protocolVersion": "2024-11-05",
           "capabilities": {},
           "clientInfo": {
               "name": "python-client",
               "version": "1.0.0"
           }
       },
       "id": 1
   }
   
   response = requests.post(base_url, headers=headers, json=init_payload)
   session_id = response.headers.get('mcp-session-id')
   print(f"Session ID: {session_id}")
   
   if not session_id:
       print("No session ID received")
       return
   
   add_payload = {
       "jsonrpc": "2.0",
       "method": "tools/call",
       "params": {
           "name": "ask_question",
           "request": "What is the main purpose of this repo?",
           "arguments": {
               "repo_path": "./grip-repo"
           }
       },
       "id": 2
   }
   with Client("http://localhost:8080/sse") as client:
        for event in client.stream(
            "mcp.prompt",
            params={"session_id": session_id, "question": "What is the main purpose of this repo?", "repo_path": "./grip-repo"}
        ):
            print(event)



async def autonomous_mcp_query(client, question):
    async with client:
        # Create a rich context for the completion
        context = f"""
        Question: {question}
        Repo path: ./grip-repo

        Available tools: ask_question, list_files, read_file, search_in_repo
        
        Please answer the question using any appropriate tools or prompts.
        """
        prompt_resource = types.Resource(
                uri="file:///grip_qa/0008.q.md",
                name="Application Logs",
                mimeType="text/plain"
            )
        
        prompt = types.PromptMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=f"Explain how this python code works:"
                        )
                    )
        # Let the MCP client autonomously decide and execute
        response = await client.complete_mcp(
            prompt_resource,
            prompt
        )
        
        return response

async def main():
    # Connect via in-memory transport
    async with Client(mcp) as client:
        # ... use the client
        result = await client.call_tool("ask_question", {"repo_path": "./grip-repo", "question": "what is the name of the repo?"})
        # response = await autonomous_mcp_query(client, "What is the main purpose of this repo?")
        # print(response)


if __name__ == "__main__":
   try:
       asyncio.run(main())
   except requests.exceptions.ConnectionError:
       print("Check MCP its not working on 8000")
   except Exception as e:
       print(f"Error: {e}")
