import pytest
import os
from unittest.mock import patch
from fastapi import HTTPException
from app.llm.providers import get_provider, OllamaProvider, OpenAIProvider

def test_provider_factory_default():
    with patch.dict(os.environ, {"LLM_PROVIDER": "ollama"}, clear=False):
        provider = get_provider()
        assert isinstance(provider, OllamaProvider)

def test_provider_factory_openai_missing_key():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": ""}, clear=False):
        with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
            get_provider()

def test_ollama_provider_init():
    provider = OllamaProvider()
    assert provider.base_url is not None
    assert provider.chat_model is not None
    assert provider.embed_model is not None

@pytest.mark.asyncio
async def test_ollama_provider_connection_error():
    provider = OllamaProvider()
    provider.base_url = "http://localhost:59999" # invalid non-existent port
    with pytest.raises(HTTPException) as exc_info:
        await provider.chat([{"role": "user", "content": "hello"}])
    assert exc_info.value.status_code == 503
    assert "Ollama connection error" in exc_info.value.detail
