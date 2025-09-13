from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

def repo_analyzer(repo_name: str):
    """List out the team members from a certain team"""
    return f"Successfully booked a stay at {repo_name}."

def list_team_users(team_name: str):
    """List out the team members from a certain specific team, for example Frontend Engineering"""
    # TODO: query from database for users of particular team
    team_members = ['Alice Johnson', 'Bob Carter', 'Charlie Nguyen', 'Diana Brooks']

    return f"These are the members from team {team_name}:{', '.join(team_members)}."

def list_teams():
    """Returns all available teams"""
    teams = ['Frontend Engineering', 'Backend Engineering']
    print('TEST')
    print(', '.join(teams))
    return f"The list of all teams in the company are {', '.joins(teams)}"

def show_team(team_name: str):
    """Gives a description for a specific team"""
    return f"{team_name} "


repo_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[repo_analyzer],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

directory_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[list_team_users, list_teams],
    prompt="You are a directory assistant who have knowledge of the available teams, team functions, and members",
    name="directory_assistant"
)

supervisor = create_supervisor(
    agents=[directory_assistant],
    model=ChatOpenAI(model="gpt-4o"),
    prompt=(
        "You act as knowledge base who helps the client synthesize information from multiple sources and analyze them.You manage a worker directory assistant."
        "Directory assistent will have information on the team functions and it's member. Assign work to them to answer the request."
    )
).compile()

for chunk in supervisor.stream(
    {
        "messages": [
            {
                "role": "user",
                "content": "What are the members of Backend Engineering team?"
            }
        ]
    }
):
    print(chunk)
    print("\n")
