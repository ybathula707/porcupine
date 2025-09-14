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

## FastAPI Ticket Management Application

The `/app` folder contains a FastAPI application for ticket management.

### Running the FastAPI Application

**Note:** Ensure the database is running in parallel using the db docker-compose command above.

#### Option 1: Local Development
```bash
cd app
uv run uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

#### Option 2: Docker
1. Build the image with `porcupine:latest` tag:
```bash
cd app
docker build -t porcupine:latest .
```

2. Start with docker-compose:
```bash
cd app
docker compose -f app/docker-compose.yml up
```

### API Access
- Local: http://localhost:8000/docs
- Docker: http://localhost/docs
- Endpoint: `POST /tickets` - Evaluate tickets with title, description, and acceptance criteria

## Frontend Application

The `/frontend` folder contains a Next.js application with a user interface for ticket content evaluation.

### Running the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at: http://localhost:3000

### Frontend Features
- Clean, responsive UI for ticket evaluation
- Form with title (text input), description (textarea), and acceptance criteria (textarea)
- Real-time form validation
- Success/error feedback
- Automatic form reset after successful submission
- Connects to FastAPI backend on port 8000

**Note:** Ensure the FastAPI backend is running on port 8000 for the frontend to work properly.
