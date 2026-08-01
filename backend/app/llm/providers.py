import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any
import httpx
from openai import AsyncOpenAI
from fastapi import HTTPException

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, model_override: str = None) -> str:
        pass
        
    @abstractmethod
    async def embed(self, texts: List[str]) -> List[List[float]]:
        pass

class OllamaProvider(LLMProvider):
    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.chat_model = os.getenv("OLLAMA_CHAT_MODEL", "qwen2.5:7b")
        self.embed_model = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, model_override: str = None) -> str:
        model_to_use = model_override if model_override else self.chat_model
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": model_to_use,
                        "messages": messages,
                        "stream": False,
                        "options": {"temperature": temperature}
                    }
                )
                response.raise_for_status()
                data = response.json()
                return data["message"]["content"]
            except httpx.RequestError as e:
                raise HTTPException(status_code=503, detail=f"Ollama connection error: {e}")
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise HTTPException(status_code=404, detail=f"Ollama model '{model_to_use}' not found. Please pull it.")
                raise HTTPException(status_code=500, detail=f"Ollama HTTP error: {e}")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            embeddings = []
            for text in texts:
                try:
                    response = await client.post(
                        f"{self.base_url}/api/embeddings",
                        json={
                            "model": self.embed_model,
                            "prompt": text
                        }
                    )
                    response.raise_for_status()
                    embeddings.append(response.json()["embedding"])
                except Exception as e:
                    raise HTTPException(status_code=503, detail=f"Ollama embedding error: {e}")
            return embeddings

class OpenAIProvider(LLMProvider):
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for OpenAIProvider")
        self.client = AsyncOpenAI(api_key=api_key)
        self.chat_model = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
        self.embed_model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.2, model_override: str = None) -> str:
        model_to_use = model_override if model_override else self.chat_model
        try:
            response = await self.client.chat.completions.create(
                model=model_to_use,
                messages=messages, # type: ignore
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI chat error: {str(e)}")

    async def embed(self, texts: List[str]) -> List[List[float]]:
        try:
            response = await self.client.embeddings.create(
                model=self.embed_model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"OpenAI embedding error: {str(e)}")

def get_provider() -> LLMProvider:
    provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
    if provider_name == "openai":
        return OpenAIProvider()
    return OllamaProvider()
