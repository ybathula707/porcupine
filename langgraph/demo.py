from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from .repo_analysis import repo_analyzer_simple
from mcp_client import read_project_file_mcp, print_conversation_summary

def repo_analyzer(repo_name: str):
    """
        Will Parse through the repos in a directory location, analyzing the file structure and dependencies.

    """
    result_json = repo_analyzer_simple()
    return f"The overview of the projects within the file system: {result_json}."

def mcp_file_summary(filename=None, projectname=None):
    """
        Use thi when you need to learn more about a file in the local repository.
        Use this to get details from the file summarized and return here.

    """
    read_project_file_mcp(file_name=filename,project_name=projectname )

def query_directory_users(team_name: str):
    """Book a flight"""
    return f"Successfully booked a flight from {team_name} )."

def query_directory_team(team_name: str):
    """Book a flight"""
    return f"Successfully booked a flight from {team_name} )."


repo_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[repo_analyzer, mcp_file_summary],
    prompt="You are a repository analysis specialist.\n"
        "Given the output from the `repo_analyzer` tool, infer the project purpose, architecture, "
        "key directories, notable files, and how dependencies shape the stack.\n"
        "Always call `repo_analyzer` first when given a repo URL. Return a concise, structured report."
    ,
    name="repo_assistant"
)

directory_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[query_directory_users,query_directory_team],
    prompt="You are a hotel booking assistant",
    name="hotel_assistant"
)

supervisor = create_supervisor(
    agents=[repo_assistant, directory_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "You manage a hotel booking assistant and a"
        "flight booking assistant. Assign work to them."
    )
).compile()

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "book a flight from BOS to JFK and a stay at McKittrick Hotel"
            }
        ]
    }
):
    print(chunk)
    print("\n")