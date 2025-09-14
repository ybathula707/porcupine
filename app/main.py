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
from agents import supervisor
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

@app.websocket("/ws/ticket/{ticket_id}/eval")
async def websocket_endpoint(websocket: WebSocket, ticket_id: int, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for streaming real-time events to the frontend for a specific ticket.
    """
    await manager.connect(websocket)
    try:
        # Query the ticket from the database
        ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
        if not ticket:
            await manager.send_personal_message(
                json.dumps({
                    "type": "error",
                    "message": f"Ticket with ID {ticket_id} not found",
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
            return
        
        # Send welcome message with ticket information
        await manager.send_personal_message(
            json.dumps({
                "type": "connection",
                "message": f"Connected to ticket evaluation stream for ticket: {ticket.title}",
                "ticket_id": ticket.id,
                "ticket_title": ticket.title,
                "timestamp": datetime.now().isoformat()
            }),
            websocket
        )

        # Create enhanced prompt using ticket content
        ticket_prompt = f"""
        Please evaluate this ticket and provide a comprehensive analysis with the following structure:
        
        TICKET DETAILS:
        Title: {ticket.title}
        Description: {ticket.description}
        Acceptance Criteria: {ticket.acceptance_criteria}
        
        Please provide your analysis in the following format, which each section as it's own paragraph:
        
        1. CODE REFERENCES:
        Identify any technical references, frameworks, libraries, APIs, databases, or code components mentioned in the ticket. Only mention relevant technical references that are explicitly stated or clearly implied - avoid unnecessary mentions.
        
        2. RECOMMENDED APPROACH:
        Provide a concise step-by-step approach to implement this ticket. Focus on the key implementation steps and technical considerations.
        
        3. TEAM MEMBER RECOMMENDATIONS:
        Based on the technical requirements and team expertise, identify specific team members who would be most knowledgeable for this task. Consider the team functions and member roles when making recommendations.
        
        Please be concise and focus on actionable insights. Do not provide unnecessary summaries.
        """

        # Stream supervisor response
        try:
            for chunk in supervisor.compile().stream(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": ticket_prompt
                        }
                    ]
                }
            ):
                # Extract meaningful content from the chunk - only AIMessage instances
                if 'supervisor' in chunk and 'messages' in chunk['supervisor']:
                    messages = chunk['supervisor']['messages']
                    for message in messages:
                        # Only process AIMessage instances, skip ToolMessage
                        if (hasattr(message, 'content') and message.content and 
                            hasattr(message, '__class__') and 
                            message.__class__.__name__ == 'AIMessage'):
                            await manager.send_personal_message(
                                json.dumps({
                                    "type": "ticket_evaluation_progress",
                                    "message": message.content,
                                    "ticket_id": ticket.id,
                                    "timestamp": datetime.now().isoformat()
                                }),
                                websocket
                            )

                # Extract meaningful content from the chunk - only AIMessage instances
                if 'directory_assistant' in chunk and 'messages' in chunk['directory_assistant']:
                    messages = chunk['directory_assistant']['messages']
                    for message in messages:
                        # Only process AIMessage instances, skip ToolMessage
                        if (hasattr(message, 'content') and message.content and 
                            hasattr(message, '__class__') and 
                            message.__class__.__name__ == 'AIMessage'):
                            await manager.send_personal_message(
                                json.dumps({
                                    "type": "directory_assistant_evaluation_progress",
                                    "message": message.content,
                                    "ticket_id": ticket.id,
                                    "timestamp": datetime.now().isoformat()
                                }),
                                websocket
                            )

            # Send completion message
            await manager.send_personal_message(
                json.dumps({
                    "type": "ticket_evaluation_complete",
                    "message": f"Ticket evaluation completed for: {ticket.title}",
                    "ticket_id": ticket.id,
                    "timestamp": datetime.now().isoformat()
                }),
                websocket
            )
            # Disconnect when done
            manager.disconnect(websocket)

        except Exception as e:
            await manager.send_personal_message(
                json.dumps({
                    "type": "ticket_evaluation_error",
                    "message": f"Error during ticket evaluation: {str(e)}",
                    "ticket_id": ticket.id,
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
