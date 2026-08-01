# Architecture

## Stack
- **Frontend**: React + Vite + Plain CSS
- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL (Supabase) + pgvector
- **LLMs**: OpenAI API / Local Ollama

## Layered Architecture
`api/` -> `services/` (Router, Skills) -> `llm/` (Providers) & `rag/` (Retriever/Embeddings) -> `db/` (Models)

## Vector DB & RAG
- Documents are chunked (500 tokens, 100 overlap).
- Embeddings stored in Supabase pgvector.
- HNSW or IVFFlat index used for similarity search.
