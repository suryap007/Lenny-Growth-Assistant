import logging
import re
from uuid import UUID
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.chat import ChatRequest, ChatResponse, ArtifactSchema
from app.services.llama_service import generate_llama_response
from app.db import crud

logger = logging.getLogger(__name__)

def parse_artifact(text: str):
    """
    Extracts markdown or html code blocks to render as artifacts.
    Returns (answer, artifact_dict)
    """
    match = re.search(r'```(markdown|html|css)\n(.*?)```', text, re.DOTALL)
    if match:
        artifact_type = match.group(1)
        content = match.group(2)
        
        # Remove the artifact from the main text answer
        answer = text.replace(match.group(0), "").strip()
        if not answer:
            answer = "Here is the artifact you requested."
            
        return answer, {
            "artifact_type": artifact_type,
            "title": "Generated Artifact",
            "content": content
        }
        
    return text, None

async def process_chat_request(request: ChatRequest, db: AsyncSession) -> ChatResponse:
    """
    Processes the chat request using the DB CRUD layer and Llama service.
    """
    session_id = request.session_id
    
    # 1. Save user message
    await crud.save_message(db, session_id, "user", request.message)
    
    # 2. Update session title if needed
    await crud.update_session_title_if_needed(db, session_id, request.message)
    
    # 3. Call LLM
    try:
        llama_answer = await generate_llama_response(request.message, str(session_id), db)
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        await db.rollback()
        raise HTTPException(status_code=503, detail="LLM Service Unavailable")
        
    # 4. Parse for artifacts
    answer, artifact_dict = parse_artifact(llama_answer)
    
    artifact_data = None
    if artifact_dict:
        artifact_data = ArtifactSchema(
            artifact_type=artifact_dict["artifact_type"],
            artifact_title=artifact_dict["title"],
            artifact_content=artifact_dict["content"]
        )
        
    # 5. Save assistant message and optional artifact
    assistant_msg = await crud.save_message(
        db, 
        session_id, 
        "assistant", 
        answer,
        artifact_type=artifact_data.artifact_type if artifact_data else None,
        artifact_content=artifact_data.artifact_content if artifact_data else None
    )
    
    if artifact_data:
        await crud.save_artifact(
            db,
            session_id,
            assistant_msg.id,
            artifact_data.artifact_type,
            artifact_data.artifact_title,
            artifact_data.artifact_content
        )
        
    # 6. Final commit
    await db.commit()
    
    return ChatResponse(
        answer=answer,
        artifact=artifact_data,
        sources=[]
    )
