from typing import Union
from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
import json
import asyncio
from datetime import datetime

from db.database import get_db, engine
from db.models import Base, Ticket
from schemas import TicketCreate, TicketResponse

app = FastAPI(title="Ticket Management API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove broken connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

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

@app.websocket("/ws/ticket/{ticket_id}/eval")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for streaming real-time events to the frontend.
    """
    await manager.connect(websocket)
    try:
        await manager.broadcast(
            json.dumps({
                "type": "ticket_evaluation_progress",
                "message": "Saving to database...",
                "timestamp": datetime.now().isoformat()
            })
        )
        
        # Keep connection alive and handle incoming messages
        while True:
            data = await websocket.receive_text()
            # Echo back any messages (can be extended for specific functionality)
            await manager.send_personal_message(
                json.dumps({
                    "type": "echo",
                    "message": f"Received: {data} for ticket {ticket_id}",
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/tickets", response_model=TicketResponse)
async def evaluate_ticket(ticket: TicketCreate, db: Session = Depends(get_db)):
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
    except OperationalError as e:
        # Broadcast error
        await manager.broadcast(
            json.dumps({
                "type": "ticket_evaluation_error",
                "message": "Database connection unavailable",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
        )
        raise HTTPException(status_code=503, detail="Database connection unavailable")
