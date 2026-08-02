# Product Requirements Document (PRD)
**Product**: Lenny Growth Assistant (Agentic Architecture)
**Date**: August 2026
**Status**: V1 (Production Ready)

---

## 🎣 1. The Hook: Why We Are Building This
**The era of the monolithic chatbot is over.** 
Users no longer want to just *chat* with their data; they want to *create* with it. Current RAG (Retrieval-Augmented Generation) applications treat every prompt as a search query, dumping massive walls of unformatted text into a narrow chat window. 

The **Lenny Growth Assistant** bridges the gap between knowledge retrieval and content creation. By utilizing a multi-agent orchestrated backend and a generative "Artifact" UI, users can extract insights from Lenny's Podcast and instantly transform them into viral essays, structural code components, or analytical summaries—all within a seamless, premium workspace.

---

## 🚨 2. The Problem Space
Founders, Product Managers, and Marketers consider Lenny's Podcast a goldmine of strategic knowledge. However, extracting actionable value from audio transcripts is broken:
1. **The Hallucination Problem**: Generic LLMs hallucinate growth metrics and attribute quotes to the wrong guests.
2. **The Formatting Problem**: When a user asks an AI to "write an essay based on the episode," the AI dumps 1,200 words into a narrow 400px chat bubble, destroying readability.
3. **The Rigid Pipeline**: Standard RAG pipelines force *every* query through a vector database. If a user asks "Debug this React code," the system wastes time searching the podcast transcripts for React code, fails, and gets confused.

---

## 🔭 3. Product Vision & Value Proposition
**Vision**: To build the ultimate autonomous growth companion—an agent that doesn't just answer questions, but acts as a junior PM, copywriter, and engineer deeply grounded in Lenny's ecosystem.

### Core Value Propositions (The "Aha!" Moments)
- **The Orchestrator**: The system *thinks* before it acts. It intercepts the user's prompt and autonomously decides whether to search the database, write an essay, or generate code.
- **The Artifact Viewer**: A revolutionary UI shift. When content is generated, the chat window smoothly slides over, opening a dedicated, syntax-highlighted workspace for long-form reading and code copying.
- **Local-First Execution**: The ability to run the entire orchestration and generation pipeline locally on an M-series Mac via Ollama, ensuring zero API costs and total privacy.

---

## 📋 4. Deep Feature Requirements

### 4.1 Agentic Orchestration (The "Pi" Engine)
- **Description**: A zero-shot intent classifier that sits in front of the application.
- **Requirements**:
  - Must intercept `POST /api/chat` requests and strip previous chat history to prevent context bias during classification.
  - Must evaluate the prompt and route it to exactly one of three isolated "Skills": `qa`, `ship30`, or `code`.
  - **Constraint**: Must achieve a >98% routing accuracy on edge-case testing to prevent RAG pipeline contamination.

### 4.2 Dynamic Skill Pipelines
Each routed intent must trigger a completely isolated execution environment.
- **Skill 1: Q&A (RAG)**: Must generate a 768-dimension embedding and execute a cosine similarity search (`<=>`) against `pgvector`. It must firmly state "I don't know" if the context chunk lacks the answer.
- **Skill 2: Ship30for30 Essayist**: Must bypass the vector DB. Must apply strict systemic constraints (1200-word limit, viral hooks, bolded headers). Must return an `artifact_type` of `markdown`.
- **Skill 3: Software Engineer**: Must generate raw programming logic and execute regex extraction to strip conversational fluff, returning an `artifact_type` of `code`.

### 4.3 Generative UI (The "Impeccable" Style)
- **Description**: The frontend must react to the payload type returned by the API.
- **Requirements**:
  - Implement a split-screen Artifact Viewer that mounts via a CSS flexbox slide-in animation (`0.4s cubic-bezier`).
  - **Markdown Rendering**: Must use `react-markdown` to safely parse and style long-form text.
  - **Code Rendering**: Must use `react-syntax-highlighter` with a dark theme (`vscDarkPlus`) to contrast against the light editorial UI.
  - The UI must adhere strictly to the **Impeccable.style** design system (Warm creams, Amber accents, pure white structural panels).

### 4.4 The LLM Toggle Switch (Provider Abstraction)
- **Description**: The backend must abstract the LLM HTTP clients.
- **Requirements**:
  - Implement an Abstract Base Class (`LLMProvider`) enforcing `chat()` and `embed()` methods.
  - Must support dynamic toggling between `httpx` calls to `localhost:11434` (Ollama) and the official `openai` Python SDK.
  - Driven entirely by a single `.env` variable (`LLM_PROVIDER`).

---

## 🗺️ 5. Key User Journeys

### Journey 1: The Tactical Marketer
1. User asks: *"Write a Ship30for30 essay about why retention is better than acquisition."*
2. The Orchestrator classifies intent as `ship30`.
3. The Ship30 skill applies viral copywriting constraints and generates the text.
4. The frontend receives the `markdown` artifact payload. The Artifact Viewer smoothly slides in, displaying a beautifully formatted, ready-to-publish essay.

### Journey 2: The Fact Checker
1. User asks: *"What is the core principle of PLG according to the transcripts?"*
2. The Orchestrator classifies intent as `qa`.
3. The RAG skill vectorizes the query, retrieves the Top-8 chunks from Supabase, and generates a grounded response.
4. The frontend renders the answer in the standard chat bubble, completely ignoring the Artifact Viewer.

---

## 📈 6. Success Metrics (KPIs)
1. **Routing Precision**: 100% pass rate on the 50-query automated benchmark (`mixed_50_results.json`).
2. **Groundedness**: 0% hallucination rate on negative-boundary RAG queries (measured via automated semantic eval).
3. **TTFB (Time to First Byte)**: < 2.5 seconds on local `qwen2.5:7b` inference.
4. **UX Engagement**: > 40% of queries trigger the Artifact Viewer, proving users are utilizing the generative features over basic chat.

---

## 🚫 7. Out of Scope (Anti-Goals)
- **Audio Generation**: We are not building text-to-speech for Lenny's voice.
- **User Authentication**: This v1 is designed for single-tenant local execution or generic public deployment. Auth (JWT, OAuth) is out of scope.
- **Database Migrations on the Fly**: Schema changes must be handled via raw SQL scripts, not dynamic ORM migrations, to keep the backend lightweight.
