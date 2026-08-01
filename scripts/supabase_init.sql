-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create chat_sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    artifact_type TEXT,
    artifact_content TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create documents table for RAG
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create document_chunks table with vector embeddings
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    content TEXT NOT NULL,
    token_count INT,
    embedding VECTOR(768), -- Default for nomic-embed-text/text-embedding-3-small might be different, but we'll use 768 for nomic and adjust if openai. For mixed, we might need a general vector or specific size. Wait, text-embedding-3-small is 1536. nomic-embed-text is 768. Let's make it 1536 and pad, or just omit the dimension size if possible? pgvector allows variable dimensions if we don't specify size, but we can't create an index on a generic vector without size. Let's stick to 1536 (OpenAI) and use nomic-embed-text at 768 by creating two columns or storing it dynamically? The prompt says "embedding VECTOR(768) or provider dimension". I will use VECTOR.
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Note: to support both 768 and 1536, pgvector allows `VECTOR` without dimension for storage, but indexing requires a dimension.
ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector;

-- Add indexes
CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
-- We'll create the HNSW index in Python once we know the dimension, or if forced to standard:
-- CREATE INDEX ON document_chunks USING hnsw (embedding vector_cosine_ops);
