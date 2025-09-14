from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TicketCreate(BaseModel):
    title: str
    description: str
    acceptance_criteria: str

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    acceptance_criteria: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
