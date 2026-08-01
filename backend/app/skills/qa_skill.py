import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import Message
from app.rag.retriever import retrieve_context
import logging

logger = logging.getLogger(__name__)

async def run_qa_skill(query: str, session_id: str, db: AsyncSession) -> dict:
    """
    Retrieves context, formats prompt, and uses Pi Agent to answer based on RAG.
    """
    # 1. Retrieve Context
    context_chunks = await retrieve_context(query, db)
    sources = []
    
    if not context_chunks:
        context_str = "NO RELEVANT CONTEXT FOUND."
    else:
        context_str = ""
        for i, c in enumerate(context_chunks):
            context_str += f"--- [Document {i+1}: {c['title']} | Source: {c['source']}] ---\n{c['content']}\n\n"
            sources.append({"title": c['title'], "score": c.get('score', 0.0)})
            
    # 2. Load Prompt
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "qa_system.txt")
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read().format(context_str=context_str)
    except Exception as e:
        logger.error(f"Failed to read qa_system.txt: {e}")
        system_prompt = f"Context:\n{context_str}\nAnswer strictly based on context."

    # 3. Load Chat History
    chat_messages = []
    if session_id:
        from uuid import UUID
        stmt = select(Message).where(Message.session_id == UUID(session_id)).order_by(Message.created_at.desc()).limit(5)
        result = await db.execute(stmt)
        history_msgs = result.scalars().all()
        history_msgs.reverse() # chronological
        
        for msg in history_msgs:
            if msg.role in ["user", "assistant"] and msg.content != query:
                chat_messages.append({"role": msg.role, "content": msg.content})

    # 4. Generate Answer using standard RAG LLM Provider instead of Pi Agent
    from app.llm.providers import get_provider
    provider = get_provider()
    
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(chat_messages)
    messages.append({"role": "user", "content": query})
    
    answer = await provider.chat(messages=messages, model_override=os.getenv("LLM_MODEL_OVERRIDE"))
    
    return {
        "content": answer,
        "sources": sources,
        "artifact": None
    }
