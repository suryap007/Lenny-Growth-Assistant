from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from uuid import UUID
from app.db.session import get_db
from app.db.models import ChatSession, Message, utcnow
from app.agents.response_models import ChatRequest, ChatResponse, SessionResponse, SessionDetailResponse
from app.agents.pi_orchestrator import route_query
from app.db import crud
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
        "ollama_chat_model": os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
    }

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
        session_id = str(request.session_id)
        user_message = request.message
        
        # 1. Save user message
        await crud.save_message(db, session_id, "user", user_message)
        
        # 2. Update session title if needed
        await crud.update_session_title_if_needed(db, session_id, user_message)
        
        # 3. Route Query via Orchestrator
        result_dict = await route_query(user_message, session_id, db)
        
        artifact_data = result_dict.get("artifact")
        artifact_type = artifact_data.get("type") if artifact_data else None
        artifact_content = artifact_data.get("content") if artifact_data else None
        artifact_title = artifact_data.get("title") if artifact_data else None
        
        # 4. Save assistant message and optional artifact
        assistant_msg = await crud.save_message(
            db, 
            session_id, 
            "assistant", 
            result_dict["content"],
            artifact_type=artifact_type,
            artifact_content=artifact_content
        )
        
        if artifact_data:
            await crud.save_artifact(
                db,
                session_id,
                assistant_msg.id,
                artifact_type,
                artifact_title,
                artifact_content
            )
            
        await db.commit()
        
        return ChatResponse(
            intent=result_dict["intent"],
            content=result_dict["content"],
            artifact=artifact_data,
            sources=result_dict["sources"]
        )

    except HTTPException:
        raise
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Unexpected error in chat_endpoint: {str(e)}\n{tb}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}\n{tb}")
