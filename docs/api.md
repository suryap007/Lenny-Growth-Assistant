# API Endpoints

## Sessions
- `GET /api/sessions`: List all sessions.
- `POST /api/sessions`: Create a new session.
- `GET /api/sessions/{id}`: Get a session with its messages.
- `DELETE /api/sessions/{id}`: Delete a session.

## Chat
- `POST /api/chat`: Send a message and get a response.
  ```json
  // Request
  { "session_id": "uuid", "message": "What is PLG?" }
  
  // Response
  {
    "answer": "...",
    "artifact": null,
    "sources": [{"title": "Episode 1", "score": 0.89}]
  }
  ```

## System
- `GET /api/health`: Health check.
- `GET /api/config`: Current provider and model settings.
