from app.llm.providers import get_provider
from typing import List

async def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate vector embeddings for a list of texts using the active provider.
    """
    provider = get_provider()
    return await provider.embed(texts)
