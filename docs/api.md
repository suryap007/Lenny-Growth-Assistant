# API Reference & Endpoints

The Lenny Growth Assistant backend is powered by FastAPI, exposing a suite of RESTful endpoints to manage conversational state, artifacts, and LLM processing. All endpoints listed below are prefixed with `/api`.

---

## 1. Chat & Inference

### `POST /api/chat`
The primary ingestion endpoint for all conversational queries. This endpoint intercepts the request, routes it through the Pi Orchestrator (Intent Classifier), dispatches the appropriate skill, logs the interaction to the database, and returns the response payload.

**Request Body (`ChatRequest`):**
```json
{
  "session_id": "uuid-string",
  "message": "Write a javascript function that parses a URL"
}
```

**Response Body (`ChatResponse`):**
```json
{
  "intent": "code",
  "content": "I have generated the javascript function for you.",
  "artifact": {
    "type": "code",
    "title": "URL Parser Function",
    "content": "function parseUrl(url) {\n  return new URL(url);\n}"
  },
  "sources": []
}
```
*Deep Dive Notes:*
- **`intent`**: Returns the bucket the orchestrator classified the query into (`qa`, `ship30`, or `code`).
- **`artifact`**: If the skill generates an artifact (code or markdown), it populates this object. The frontend uses `artifact.type` to determine which renderer (`react-syntax-highlighter` vs `react-markdown`) to mount.
- **`sources`**: If the intent is `qa`, this array returns the `pgvector` chunks retrieved during the semantic search, including scores and titles for UI attribution.

---

## 2. Session Management

Conversations are stateful and persistent. Sessions track the lifecycle of a single continuous chat.

### `POST /api/sessions`
Creates a brand new conversational session. The title is initially set to `"New Chat"`. The backend will automatically update this title based on the first user query.

**Response Body (`SessionResponse`):**
```json
{
  "id": "uuid-string",
  "title": "New Chat",
  "created_at": "2026-08-01T21:00:00Z",
  "updated_at": "2026-08-01T21:00:00Z"
}
```

### `GET /api/sessions`
Retrieves a list of all active sessions in the database, ordered chronologically by `updated_at` descending. This is used to populate the frontend Sidebar.

**Response Body:**
```json
[
  {
    "id": "uuid-string",
    "title": "Debugging Promise Chains",
    "created_at": "2026-08-01T21:00:00Z",
    "updated_at": "2026-08-01T21:05:00Z"
  }
]
```

### `GET /api/sessions/{session_id}`
Retrieves a specific session, performing a SQL join (`selectinload`) to pull in all associated messages. This reconstructs the chat history when a user clicks a session in the Sidebar.

**Response Body (`SessionDetailResponse`):**
```json
{
  "id": "uuid-string",
  "title": "Debugging Promise Chains",
  "created_at": "2026-08-01T21:00:00Z",
  "updated_at": "2026-08-01T21:05:00Z",
  "messages": [
    {
      "id": "msg-uuid",
      "role": "user",
      "content": "Debug this javascript promise chain",
      "artifact_type": null,
      "artifact_content": null,
      "created_at": "2026-08-01T21:01:00Z"
    },
    {
      "id": "msg-uuid",
      "role": "assistant",
      "content": "Here is the debugged code.",
      "artifact_type": "code",
      "artifact_content": "console.log('Fixed');",
      "created_at": "2026-08-01T21:01:10Z"
    }
  ]
}
```

### `DELETE /api/sessions/{session_id}`
Hard deletes a session. Thanks to cascading foreign keys in the PostgreSQL schema, all associated messages are also wiped cleanly.

**Response Body:**
```json
{
  "status": "deleted"
}
```

---

## 3. System & Configuration

### `GET /api/health`
A standard readiness probe to verify the backend is alive.

**Response Body:**
```json
{
  "status": "ok"
}
```

### `GET /api/config`
Exposes the backend's current LLM Provider state. This endpoint reads the `.env` variables and tells the frontend which models and abstractions are currently routing logic (e.g., Ollama vs. OpenAI). The UI surfaces this data in the Top Bar.

**Response Body:**
```json
{
  "llm_provider": "ollama",
  "openai_chat_model": "gpt-4o-mini",
  "ollama_chat_model": "qwen2.5:7b"
}
```
