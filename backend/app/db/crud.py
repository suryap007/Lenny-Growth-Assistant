from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Message, Artifact, ChatSession, utcnow
from uuid import UUID
from typing import Optional

async def save_message(
    db: AsyncSession, 
    session_id: UUID, 
    role: str, 
    content: str, 
    artifact_type: Optional[str] = None, 
    artifact_content: Optional[str] = None
) -> Message:
    msg = Message(
        session_id=session_id,
        role=role,
        content=content,
        artifact_type=artifact_type,
        artifact_content=artifact_content,
        created_at=utcnow()
    )
    db.add(msg)
    await db.flush()
    return msg

async def update_session_title_if_needed(db: AsyncSession, session_id: UUID, message_content: str):
    result = await db.execute(select(ChatSession).where(ChatSession.id == session_id))
    session = result.scalar_one_or_none()
    
    if session and (session.title == "New Chat" or not session.title):
        title = message_content[:40] + ("..." if len(message_content) > 40 else "")
        session.title = title
        await db.flush()

async def save_artifact(
    db: AsyncSession, 
    session_id: UUID, 
    message_id: UUID, 
    artifact_type: str, 
    title: str, 
    content: str
) -> Artifact:
    artifact = Artifact(
        session_id=session_id,
        message_id=message_id,
        artifact_type=artifact_type,
        title=title,
        content=content,
        created_at=utcnow()
    )
    db.add(artifact)
    await db.flush()
    return artifact
