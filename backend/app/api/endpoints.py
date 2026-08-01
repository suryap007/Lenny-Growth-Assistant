from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.db.session import get_db
from app.db.models import ChatSession, Message
from app.schemas.chat import ChatRequest, ChatResponse, SessionResponse, SessionDetailResponse
from app.services.chat_service import process_chat_request
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/config")
async def get_config():
    return {
        "llm_provider": os.getenv("LLM_PROVIDER", "ollama"),
        "openai_chat_model": os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        "ollama_chat_model": os.getenv("OLLAMA_CHAT_MODEL", "llama3.1:8b")
    }

from app.db.models import ChatSession, Message, utcnow

@router.post("/sessions", response_model=SessionResponse)
async def create_session(db: AsyncSession = Depends(get_db)):
    now = utcnow()
    new_session = ChatSession(title="New Chat", created_at=now, updated_at=now)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    return new_session

@router.get("/sessions", response_model=list[SessionResponse])
async def list_sessions(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).order_by(ChatSession.updated_at.desc()))
    return result.scalars().all()

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Sort messages by created_at explicitly just in case
    session.messages.sort(key=lambda x: x.created_at)
    return session

@router.delete("/sessions/{session_id}")
async def delete_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(session)
    await db.commit()
    return {"status": "deleted"}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await process_chat_request(request, db)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in chat_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while processing your request.")
