import os
from app.services.pi_agent_service import run_agent
import logging

logger = logging.getLogger(__name__)

async def run_ship30_skill(query: str) -> dict:
    """
    Generates a Ship30for30 styled essay.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "ship30_system.txt")
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except Exception as e:
        logger.error(f"Failed to read ship30_system.txt: {e}")
        system_prompt = "You are a Ship30for30 essay writer. Write a viral essay."

    answer = await run_agent(prompt=query, system_prompt=system_prompt)
    
    # Clean up backticks if the LLM wraps the essay in a markdown code block
    clean_answer = answer.strip()
    if clean_answer.startswith("```markdown"):
        clean_answer = clean_answer[11:]
    elif clean_answer.startswith("```md"):
        clean_answer = clean_answer[5:]
    elif clean_answer.startswith("```"):
        clean_answer = clean_answer[3:]
        
    if clean_answer.endswith("```"):
        clean_answer = clean_answer[:-3]
        
    clean_answer = clean_answer.strip()
    
    return {
        "content": "I have generated your Ship30for30 essay.",
        "sources": [],
        "artifact": {
            "type": "markdown",
            "title": "Ship30for30 Essay",
            "content": clean_answer
        }
    }
