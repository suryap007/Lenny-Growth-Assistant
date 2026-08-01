import os
import re
from app.services.pi_agent_service import run_agent
import logging

logger = logging.getLogger(__name__)

async def run_code_skill(query: str) -> dict:
    """
    Generates code/UI artifacts using Pi Coding Agent.
    """
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "code_system.txt")
    try:
        with open(prompt_path, "r") as f:
            system_prompt = f.read()
    except Exception as e:
        logger.error(f"Failed to read code_system.txt: {e}")
        system_prompt = "You are a coding assistant. Return code wrapped in a markdown code block."

    raw_answer = await run_agent(prompt=query, system_prompt=system_prompt)
    
    # Extract artifact from raw answer
    match = re.search(r'```(\w+)\n(.*?)```', raw_answer, re.DOTALL)
    
    if match:
        artifact_type = match.group(1)
        content = match.group(2)
        answer = raw_answer.replace(match.group(0), "").strip()
        if not answer:
            answer = "Here is the code artifact you requested."
            
        return {
            "content": answer,
            "sources": [],
            "artifact": {
                "type": artifact_type,
                "title": "Code Artifact",
                "content": content
            }
        }
        
    return {
        "content": raw_answer,
        "sources": [],
        "artifact": None
    }
