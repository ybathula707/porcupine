from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
import os
import asyncio
# a dcitionary of server name to configurations
"""
Env variables you need to set to run this server. Set in your terminal:

FS_BASE_DIRECTORY=absolute path to the file system you want mcp to read from
OPENAI_API_KEY=duh
MCP_SERVER_LOCATION=absolute file path of mcp_server, where it's running

TIP: Just clone the the server in the same place are your test_repos directory.
porject repo for mcp server: https://github.com/cyanheads/filesystem-mcp-server 


/Users/yoshi/Desktop/demo_repos/filesystem-mcp-server/dist/index.js
"""

FS_BASE_DIRECTORY=os.getenv("FS_BASE_DIRECTORY")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
MCP_SERVER_LOCATION=os.getenv("MCP_SERVER_LOCATION")

mcp_client= MultiServerMCPClient(
    {
    "filesystem": {
        "command": "node",
        "args": [MCP_SERVER_LOCATION],
        "transport": "stdio",
        "env": {
            "MCP_LOG_LEVEL": "info",
            "FS_BASE_DIRECTORY": FS_BASE_DIRECTORY, 
            "OPENAI_API_KEY": OPENAI_API_KEY,
        }
    }
})


def extract_final_response(response):
    """Extract the final AI response from LangGraph output"""
    messages = response.get('messages', [])
    
    # Get the last AIMessage with actual content (not tool calls)
    for message in reversed(messages):
        if (hasattr(message, 'content') and 
            message.content and 
            message.content.strip() and 
            not getattr(message, 'tool_calls', None)):
            return message.content
    
    return "No final response found"

def print_conversation_summary(response):
    """Print a clean summary of the agent conversation"""
    messages = response.get('messages', [])
    
    print("🧑 USER REQUEST:")
    for msg in messages:
        if hasattr(msg, 'content') and 'Read the contents of' in str(msg.content):
            print(f"   {msg.content}\n")
            break
    
    print("🤖 AI FINAL ANSWER:")
    final_answer = extract_final_response(response)
    print(f"   {final_answer}\n")

    print("📊 CONVERSATION STATS:")
    ai_messages = sum(1 for msg in messages if type(msg).__name__ == "AIMessage")
    tool_messages = sum(1 for msg in messages if type(msg).__name__ == "ToolMessage")
    errors = sum(1 for msg in messages if type(msg).__name__ == "ToolMessage" and "Error:" in str(msg.content))
    
    print(f"   • AI Messages: {ai_messages}")
    print(f"   • Tool Calls: {tool_messages}")  
    print(f"   • Errors: {errors}")


async def read_project_file_mcp(file_name: str, project_name: str=None, file_path: str=FS_BASE_DIRECTORY):
    # Use the agent
    tools =  await mcp_client.get_tools()
    mcp_agent = create_react_agent("openai:gpt-4o", tools)

    response =  await mcp_agent.ainvoke({
        "messages": [f"Read the contents of {file_name} from the {project_name} project. Return the file contents. You can begin searching for this file at the complete projects directory {FS_BASE_DIRECTORY}. Begin looking inside the {project_name} directory for [{file_name}]"]
    })
    #print_conversation_summary(response)
    return response

# async def test():
#     # Get tools from the MCP server
#    response = await read_project_file_mcp(file_name="question_processor.py", project_name="aiskus" )
#    print_conversation_summary(response)
# asyncio.run(test())
