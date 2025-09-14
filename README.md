# porcupine
Spike Investigations

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


### Langgraph setup
```
pip install -U langgraph langsmith langgraph_supervisor
pip install -U "langchain[openai]"
```


### Database setup
directory db setup:
```
# can put in ~/.zshrc
export POSTGRES_DB=directory
export POSTGRES_USER=admin
export POSTGRES_PASSWORD=example
```

to start the db
```
docker compose -f db/docker-compose.yml up
```

to access db from terminal requires postgresql (brew), run
```
PGPASSWORD=example psql -h localhost -p 5432 -U admin -d directory
```
