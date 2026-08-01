import os
import httpx
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

async def run_agent(prompt: str = None, system_prompt: str = None, chat_messages: list = None) -> str:
    """
    Runs the Pi Coding Agent against the Ollama backend.
    """
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    if chat_messages:
        messages.extend(chat_messages)
        
    if prompt:
        messages.append({"role": "user", "content": prompt})

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                f"{base_url}/api/chat",
                json={
                    "model": model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": 0.2}
                }
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"].strip()
        except httpx.RequestError as e:
            logger.error(f"Ollama connection error: {e}")
            raise HTTPException(status_code=503, detail=f"Ollama connection error: {e}")
        except httpx.HTTPStatusError as e:
            logger.error(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Ollama model '{model}' not found. Please pull it using 'ollama pull {model}'.")
            raise HTTPException(status_code=500, detail=f"Ollama HTTP error: {e}")
