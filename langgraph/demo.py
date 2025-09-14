from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor
from repo_analysis import repo_analyzer_simple
from mcp_client import read_project_file_mcp, print_conversation_summary
from langchain_core.tools import tool

# db
from sqlalchemy import create_engine, text
import asyncio
def directory_db_query(query_string):
    print("executing db query for directory db: " + query_string)
    results = []
    try:
        engine = create_engine('postgresql+psycopg2://admin:example@localhost:5432/directory')
        connection = engine.connect()
        my_query = text(query_string)
        results = connection.execute(my_query).fetchall()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return results

@tool
def repo_analyzer():
    """
        Use this when you need to understand the structure of a codebase as part of the first repository analysis a user makes.
        Will Parse through the code base and return a report of key details of the projects located there.
        Format of each project summary will be like
        Project:
        Readme:
        Key Files: 
        Dependencies:
        Directories:
        You can use the names form the  of the key files response to inform the specific calls made to the mcp_file_summary tool. 

    """
    result = repo_analyzer_simple()
    return f"The overview of the projects within the file system: {result}."

@tool
def mcp_file_summary(filename: str, projectname: str):
    """
    Use this when trying to build more context for any repository context you need. 
    Pass parameters filename=name on the file and projectname=name of the target project in original user ticket or prompt
    Returns the contents of the file from this project.
    """
    try:
        # Run the async function in a new event loop
        response = asyncio.run(read_project_file_mcp(file_name=filename, project_name=projectname))
        return f"The file contents of {filename} from {projectname}: {response}"
    except Exception as e:
        return f"Error reading {filename} from {projectname}: {str(e)}"

repo_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[repo_analyzer, mcp_file_summary],
    prompt="""You are a specialized repository analysis expert focused on understanding codebases and providing actionable insights.
## CORE OBJECTIVES
Your primary goal is to analyze repositories and provide comprehensive insights about specific services or components within the codebase. You have access to tools to do the following:
You will also return as part of this report, the toolcalls made along with the parameters sent to those tool calls.

1. **Understand the Project Structure**: Use repo_analyzer to get an overview of all projects in the repository and to collect the names of  key files 
2. **Read File contents**: Use mcp_file_summary to read specific files for detailed context when needed. Further details

## TOOL CALL PARAMETERS
Tool call parameters:
- repo_analyzer(): Does not take any parameters, just returns summary of all projects in repo
        Will Parse through the code base and return a report of key details of the projects located there.
        Format of each project summary will be like
        Project:
        Readme:
        Key Files: 
        Dependencies:
        Directories:
        You can use the names from the of the key files response to inform the specific calls made to the mcp_file_summary tool. 
- mcp_file_summary():
    Pass parameters:
    - projectname=project_name where project_name is the target project from the original user prompt
    - filename=file_name, where file_name is a valid file name in the target project, deduced from the list of Key Files 


## TOOL USAGE PARAMAETERS GUIDELINES
- **repo_analyzer()**: no parameters needed - it analyzes the entire repository structure
- **mcp_file_summary(filename, projectname)**: Use when you need to understand specific files
  - Always specify both filename and projectname parameters
  - Read key files like README.md, main entry points, configuration files, or any files that reference the target service
  - Don't read every file - be strategic and focus on files that will provide the most relevant context

  Return the exact toolcall you are making, alongside the passed parameters to those tools as part of the response. 
""",
    name="repo_assistant"
)

def list_team_users(team_name: str):
    """List out the team members from a certain specific team, for example Frontend Engineering"""
    team_members_query_result = directory_db_query(f"SELECT users.name FROM users JOIN teams ON users.team_id = teams.id WHERE teams.name = \'{team_name}\'")
    team_members = [f"{item[0]}" for item in team_members_query_result]

    return f"These are the members from team {team_name}:{', '.join(team_members)}."

def list_teams():
    """Returns all available teams in exact format."""
    teams_query_result = directory_db_query("SELECT name FROM teams")
    teams = [item[0] for item in teams_query_result]

    return f"The list of all teams in the company are {', '.join(teams)}"

def show_team(team_name: str):
    """Gives a description for only one specific team. For multiple teams, need to call this tool repeatedly"""
    team_query_result = directory_db_query(f"SELECT name, team_function FROM teams WHERE name = '{team_name}' LIMIT 1")
    if len(team_query_result) == 1:
        t = team_query_result[0]
        return f"team {t.name} has the following responsibilities: {t.team_function}"
    else:
        return f"cannot locate details for this specific team with name {team_name}"


directory_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[list_team_users, show_team, list_teams],
    prompt="You are a directory assistant who have knowledge of the available teams, team functions, and members. In order to get team details and members, you have to provide the exact team name from the team list. If the team name closely resembles the team role, you can coerce to your exact team name and note the difference",
    name="directory_assistant"
)

supervisor = create_supervisor(
    agents=[repo_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "You act as knowledge base who helps the client synthesize information from multiple sources and analyze them.You manage a worker directory assistant."
        "Directory assistent will have information on the team functions and it's member. Assign work to them to answer the request."
        "You also manage a worker repo assistant which manages source information from a codebase."
        "The Repo assistant will contain any information about the codebase contained within a file system, as well as abilities to read specific files you require for mor context. Assign work to them to answer the request."
        "Include in the report, the tool calls made and the parameters passed to those tool calls"
    )
).compile()

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "What changes do I need to make to asikus project in order to make the project's client asychronous? I am looking at the question_processor.py file of the project."
            }
        ]
    }
):
    print(chunk)
    print("\n")



# async def test_sync_mcp_file_summary():
#     """Test the synchronous mcp_file_summary function"""
#     print("Testing sync mcp_file_summary...")
    
#     try:
#         result = mcp_file_summary("README.md", "aiskus")
#         print(result)
#     except Exception as e:
#         print(f"ERROR: {e}")
#         import traceback
#         traceback.print_exc()

# # Run the test
# if __name__ == "__main__":
#     # Comment out your supervisor stream for now and run this test
#     print("Running MCP file summary test...")
#     test_sync_mcp_file_summary()
