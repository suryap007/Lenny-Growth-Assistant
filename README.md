# Lenny Growth Assistant

A ChatGPT-like conversational web application grounded on Lenny's Podcast transcripts.

## Features
- Local & Cloud LLMs (Ollama & OpenAI)
- RAG using Supabase pgvector
- Multi-session memory
- Markdown and HTML/CSS artifact generation
- Ship30for30 style essay generation

## Prerequisites
- Node.js (v18+)
- Python 3.10+
- Supabase project (for PostgreSQL + pgvector)
- Ollama installed locally

## Setup

1. **Clone & Env Setup**
   ```bash
   cp .env.example .env
   # Fill in your Supabase connection string and API keys
   ```

2. **Install Dependencies**
   ```bash
   # Backend
   pip install -r requirement.txt
   
   # Frontend
   cd frontend
   npm install
   cd ..
   ```

3. **Database Initialization**
   Run the SQL commands in `scripts/supabase_init.sql` against your Supabase database to set up tables and the `vector` extension.

4. **Install Ollama Models**
   ```bash
   ollama pull llama3.1:8b
   ollama pull nomic-embed-text
   ```

5. **Run Application**
   In one terminal window, start the backend:
   ```bash
   make backend
   ```
   
   In another terminal window, start the frontend:
   ```bash
   make frontend
   ```
   
   * Frontend runs on http://localhost:5173
   * Backend runs on http://localhost:8000

## Ingestion
To ingest transcripts:
```bash
make ingest
```

## Troubleshooting
- If Ollama is not working, ensure the base URL in `.env` matches your local setup (e.g. `http://localhost:11434`).
- If pgvector fails, ensure you ran the init script on Supabase.
