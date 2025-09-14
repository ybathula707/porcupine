from typing import Union
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from db.database import get_db, engine
from db.models import Base, Ticket
from schemas import TicketCreate, TicketResponse

app = FastAPI(title="Ticket Management API", version="1.0.0")

# Initialize database tables on startup
@app.on_event("startup")
async def startup_event():
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully")
    except OperationalError as e:
        print(f"Database connection failed: {e}")

@app.get("/")
def read_root():
    return {"Hello": "World", "message": "Ticket Management API is running"}

@app.post("/tickets", response_model=TicketResponse)
def evaluate_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
    """
    Evaluate a new ticket with title, description, and acceptance criteria.
    """
    try:
        db_ticket = Ticket(
            title=ticket.title,
            description=ticket.description,
            acceptance_criteria=ticket.acceptance_criteria
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except OperationalError:
        raise HTTPException(status_code=503, detail="Database connection unavailable")
