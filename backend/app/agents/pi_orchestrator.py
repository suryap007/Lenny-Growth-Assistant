import time
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.agents.intents import classify_intent, Intent
from app.skills.qa_skill import run_qa_skill
from app.skills.ship30_skill import run_ship30_skill
from app.skills.code_skill import run_code_skill

logger = logging.getLogger(__name__)

async def route_query(query: str, session_id: str, db: AsyncSession = None) -> dict:
    """
    Main orchestration entrypoint. Classifies intent and routes to specialized skill.
    """
    start_time = time.time()
    intent = None
    
    try:
        # 1. Detect Intent
        intent = await classify_intent(query)
        logger.info(f"Intent detected: {intent.value}")
        
        # 2. Route to Skill
        if intent == Intent.SHIP30:
            result = await run_ship30_skill(query)
        elif intent == Intent.CODE:
            result = await run_code_skill(query)
        else:
            if not db:
                raise ValueError("Database session is required for QA skill")
            result = await run_qa_skill(query, session_id, db)
            
        execution_time = time.time() - start_time
        logger.info(f"Execution completed in {execution_time:.2f}s for query: {query}")
        
        # 3. Standardized Response
        return {
            "intent": intent.value,
            "content": result.get("content", ""),
            "artifact": result.get("artifact"),
            "sources": result.get("sources", [])
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Error during orchestration (Intent: {intent}, Time: {execution_time:.2f}s): {e}")
        raise e
