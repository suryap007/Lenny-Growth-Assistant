# System Architecture Document

## Overview

The Lenny Growth Assistant architecture is designed around three primary pillars:
1. **Agentic Routing**: Dynamic intent classification that circumvents traditional monolithic chat pipelines.
2. **Provider Abstraction**: A seamless toggle system between local and cloud LLMs.
3. **Reactive UI State**: A frontend that scales and animates natively based on the type of Artifact payload returned by the server.

---

## 1. Database Schema

We leverage **Supabase PostgreSQL** alongside the `pgvector` extension to handle both relational session data and high-dimensional semantic search.

### `sessions` Table
- `id` (UUID): Primary key.
- `title` (VARCHAR): Auto-generated summarization of the session's topic.
- `created_at` (TIMESTAMP): Creation time.

### `messages` Table
- `id` (UUID): Primary key.
- `session_id` (UUID): Foreign key linking to the `sessions` table.
- `role` (VARCHAR): `user` or `assistant`.
- `content` (TEXT): The raw conversational text.
- `artifact_type` (VARCHAR): Optional column dictating how the frontend should parse the message (`markdown`, `code`).
- `artifact_content` (TEXT): Optional payload containing the generated artifact data.
- `created_at` (TIMESTAMP): Message creation time.

### `transcripts` Table (Vector Store)
- `id` (UUID): Primary key.
- `content` (TEXT): A chunked segment of a Lenny podcast transcript.
- `embedding` (VECTOR(768)): The vectorized representation of the `content` chunk (using `nomic-embed-text` or similar).
- `metadata` (JSONB): Episode details, guest names, timestamps.

---

## 2. API Endpoints (FastAPI)

The backend (`app.main`) exposes a RESTful API wrapped in standard OpenAPI specs.

- `POST /api/chat`: The primary ingestion endpoint. It receives the `session_id` and the user's `message`.
- `GET /api/sessions`: Retrieves all user sessions, ordered by most recent.
- `GET /api/sessions/{session_id}/messages`: Retrieves the full conversation history for a specific session to reconstruct the context window.
- `DELETE /api/sessions/{session_id}`: Hard deletes a session and cascades deletes its associated messages.

---

## 3. Agentic Routing Logic (The Orchestrator)

The core logic of the application lives inside the `pi_orchestrator.py` engine. Instead of forcing every query through a retrieval chain, we use an LLM zero-shot classifier.

### The Pipeline
1. **Intent Classification**: When a query hits `/api/chat`, the `pi_orchestrator` strips out system context and sends the raw query to an LLM intent router with a strict system prompt (`intent_router.txt`).
2. **Labeling**: The LLM classifies the query into one of three buckets: `qa`, `ship30`, or `code`.
3. **Skill Dispatch**:
   - **`qa` (RAG)**: The query is routed to `qa_skill.py`. It embeds the query, performs a cosine similarity search against pgvector, and injects the context into the prompt.
   - **`ship30`**: The query is routed to `ship30_skill.py`. It bypasses the vector DB and loads the highly opinionated `ship30_system.txt` prompt to generate a 1200-word viral essay. It returns a `markdown` artifact payload.
   - **`code`**: The query is routed to `code_skill.py`. It loads the `code_system.txt` prompt, generates software logic, and extracts the raw code via regex. It returns a `code` artifact payload.

---

## 4. LLM Toggle Switch implementation

The `LLMProvider` abstraction (`providers.py`) isolates the application logic from the underlying LLM HTTP clients.

### Interface Design
An abstract base class `LLMProvider` defines two required async methods:
- `chat(messages: list, temperature: float) -> str`
- `embed(texts: list) -> list`

### Concrete Implementations
- **`OllamaProvider`**: Uses the `httpx` library to communicate with `localhost:11434`. Handles graceful fallback if the model is missing.
- **`OpenAIProvider`**: Uses the official `openai` Python async client to communicate with OpenAI's API.

### The Toggle
A factory function `get_provider()` reads the `LLM_PROVIDER` environment variable during application startup. If set to `"ollama"`, the entire application—including the orchestrator, skills, and embedding pipeline—switches to local execution. If set to `"openai"`, it utilizes GPT-4o. This allows the evaluator to test locally without incurring API costs.
