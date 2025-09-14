from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

# db
from sqlalchemy import create_engine, text

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

def repo_analyzer(repo_name: str):
    """List out the team members from a certain team"""
    return f"Successfully booked a stay at {repo_name}."

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


repo_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[repo_analyzer],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
)

directory_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[list_team_users, show_team, list_teams],
    prompt="You are a directory assistant who have knowledge of the available teams, team functions, and members. In order to get team details and members, you have to provide the exact team name from the team list. If the team name closely resembles the team role, you can coerce to your exact team name and note the difference",
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
                "content": "What are things the qa team do in my company?"
            }
        ]
    }
):
    print(chunk)
    print("\n")
