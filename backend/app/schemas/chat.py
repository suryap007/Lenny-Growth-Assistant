from pydantic import BaseModel
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
    answer: str
    artifact: Optional[ArtifactSchema] = None
    sources: List[SourceSchema] = []

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
    artifact_type: Optional[str]
    artifact_content: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class SessionDetailResponse(SessionResponse):
    messages: List[MessageResponse] = []
