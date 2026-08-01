# Lenny Growth Assistant

The Lenny Growth Assistant is a full-stack, agentic AI product that enables users to engage in context-aware conversations based on Lenny's Podcast transcripts. Built with a responsive "Impeccable" light-theme UI, the assistant natively handles dynamic markdown generation, coding requests, and viral essay formatting via a sophisticated multi-agent backend.

## 🏗️ Architecture Overview

The application utilizes a modular, multi-tier architecture:
- **Frontend (React/Vite)**: A state-of-the-art Single Page Application (SPA) utilizing CSS Flexbox animations and dynamic artifact rendering (via React Markdown and React Syntax Highlighter).
- **Backend (FastAPI)**: An async Python backend that exposes endpoints for chat sessions and message handling.
- **LLM Abstraction Layer**: The system can dynamically toggle between local (`Ollama`) and cloud (`OpenAI`) models via an abstracted `LLMProvider` interface.
- **Agentic Routing (`Pi Orchestrator`)**: User queries are evaluated by an LLM-based zero-shot intent classifier and routed to specialized "Skills" (`qa_skill`, `ship30_skill`, `code_skill`) rather than a monolithic RAG pipeline.
- **Database (Supabase PostgreSQL + pgvector)**: Stores session metadata, conversational history, and vector embeddings of transcript chunks for semantic search.

## 🚀 Deployment & Local Execution

Follow these step-by-step instructions to deploy the Lenny Growth Assistant locally.

### 1. Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (v3.10+ recommended)
- **Ollama** installed locally and running
- **Supabase** account (or local Supabase instance)

### 2. Environment Variables Setup
Create a `.env` file in the root of the project. **Do not push your keys to GitHub.**

```env
# Database Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key

# LLM Toggle Switch
# Options: "ollama" or "openai"
LLM_PROVIDER=ollama

# Ollama Specific
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=qwen2.5:7b
OLLAMA_EMBED_MODEL=nomic-embed-text

# OpenAI Specific (Optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_CHAT_MODEL=gpt-4o-mini
OPENAI_EMBED_MODEL=text-embedding-3-small
```

### 3. Dependencies Installation

**Backend Setup:**
Open a terminal in the `backend/` directory:
```bash
cd backend
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

**Frontend Setup:**
Open a new terminal in the `frontend/` directory:
```bash
cd frontend
npm install
```

### 4. Running the Application

**Start the Local Models:**
Ensure Ollama is running and you have pulled the required models:
```bash
ollama pull qwen2.5:7b
ollama pull nomic-embed-text
```

**Start the Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Start the Frontend:**
```bash
cd frontend
npm run dev
```

The UI will be accessible at `http://localhost:5173/`.

## 📂 Documentation

Additional detailed documentation can be found in the `docs/` folder:
- **`docs/PRD.md`**: Product Requirements Document outlining the software building process.
- **`docs/architecture.md`**: Deep dive into the database schema, agentic routing, and LLM toggle logic.
- **`docs/design.md`**: UI/UX design rationale detailing the "Impeccable" styling choices.
