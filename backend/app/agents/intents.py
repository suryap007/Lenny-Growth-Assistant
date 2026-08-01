from enum import Enum
import os
import logging
from app.services.pi_agent_service import run_agent

logger = logging.getLogger(__name__)

class Intent(str, Enum):
    QA = "qa"
    SHIP30 = "ship30"
    CODE = "code"

async def classify_intent(query: str) -> Intent:
    """
    Uses Pi Coding Agent to classify the intent of a query.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "intent_router.txt")
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except Exception as e:
        logger.error(f"Failed to read intent_router.txt: {e}")
        return Intent.QA # Fallback

    try:
        result = await run_agent(query, system_prompt=system_prompt)
        result_lower = result.strip().lower()
        
        if "ship30" in result_lower:
            return Intent.SHIP30
        elif "code" in result_lower:
            return Intent.CODE
        else:
            return Intent.QA
    except Exception as e:
        logger.error(f"Failed to classify intent: {e}")
        return Intent.QA
