from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import DocumentChunk, Document
from app.rag.embeddings import generate_embeddings
from typing import List, Dict, Any
from app.llm.providers import get_provider
import json

async def rewrite_query(query: str) -> str:
    """Uses LLM to optimize the retrieval query by extracting entities and removing filler."""
    provider = get_provider()
    prompt = f"""You are a search query optimizer. 
Convert the following conversational question into a concise set of keywords and named entities optimized for vector search.
Remove filler words like 'what is', 'how to', 'tell me about'.
Output ONLY the optimized query string. No quotes, no markdown, no explanation.

Original Query: {query}
Optimized Query:"""
    try:
        messages = [{"role": "user", "content": prompt}]
        response = await provider.chat(messages, temperature=0.0)
        optimized = response.strip(' "\'')
        print(f"Original: '{query}' -> Optimized: '{optimized}'")
        return optimized if optimized else query
    except Exception as e:
        print(f"Query rewrite error: {e}")
        return query

async def retrieve_context(query: str, db: AsyncSession, top_k: int = 8, threshold: float = 0.65) -> List[Dict[str, Any]]:
    # Rewrite the query
    optimized_query = await rewrite_query(query)
    
    # Generate embedding for the query
    # Generate embedding for the query
    query_embeddings = await generate_embeddings([optimized_query])
    query_vector = query_embeddings[0]
    
    # Similarity search using vector cosine distance (pgvector uses <-> for L2, <=> for cosine)
    # Cosine distance: 1 - cosine_similarity
    # We want closest distance
    stmt = (
        select(DocumentChunk, Document.title, Document.source, DocumentChunk.embedding.cosine_distance(query_vector).label("distance"))
        .join(Document, Document.id == DocumentChunk.document_id)
        .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
        .limit(top_k * 2) # Fetch more for optional deduplication/filtering
    )
    
    result = await db.execute(stmt)
    rows = result.all()
    
    # Deduplicate and filter by threshold (distance < (1 - threshold))
    seen_chunks = set()
    retrieved = []
    
    for row in rows:
        chunk, doc_title, doc_source, distance = row
        similarity = 1 - distance
        
        if similarity < threshold:
            continue
            
        # Optional: Deduplicate by exact content or document id + chunk index
        chunk_key = (chunk.document_id, chunk.chunk_index)
        if chunk_key not in seen_chunks:
            seen_chunks.add(chunk_key)
            retrieved.append({
                "content": chunk.content,
                "title": doc_title,
                "source": doc_source,
                "score": float(similarity),
                "metadata": chunk.metadata_ or {}
            })
            
        if len(retrieved) >= top_k:
            break
            
    return retrieved
