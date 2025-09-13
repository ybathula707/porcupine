from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

def repo_analyzer(repo_name: str):
    """Book a hotel"""
    return f"Successfully booked a stay at {repo_name}."

def query_directory_users(team_name: str):
    """Book a flight"""
    return f"Successfully booked a flight from {team_name} )."

def query_directory_team(team_name: str):
    """Book a flight"""
    return f"Successfully booked a flight from {team_name} )."


repo_assistant = create_react_agent(
    model="openai:gpt-4o",
    tools=[repo_analyzer],
    prompt="You are a flight booking assistant",
    name="flight_assistant"
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