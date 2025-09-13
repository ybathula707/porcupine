# porcupine
Spike Investigations

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

db setup:
```
docker compose -f db/docker-compose.yml up
```

to access db, run
```
PGPASSWORD=example psql -h localhost -p 5432 -U admin -d directory
```
