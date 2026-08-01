from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class ArtifactSchema(BaseModel):
    artifact_type: str
    artifact_title: str
    artifact_content: str

class ChatRequest(BaseModel):
    session_id: UUID
    message: str

class SourceSchema(BaseModel):
    title: str
    score: float

class ChatResponse(BaseModel):
    intent: str
    content: str
    artifact: Optional[dict] = None
    sources: Optional[list] = None

class SessionResponse(BaseModel):
    id: UUID
    title: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    artifact_type: Optional[str] = None
    artifact_content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    messages: List[MessageResponse] = []
