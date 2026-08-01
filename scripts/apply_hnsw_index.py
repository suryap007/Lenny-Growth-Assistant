import asyncio
import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent / "backend"))

from app.db.session import engine
from sqlalchemy import text

async def apply_hnsw_index():
    print("Applying HNSW Index to document_chunks...")
    async with engine.begin() as conn:
        # We need to alter the column to VECTOR(768) and create the index
        # This requires dropping the old index if it exists, or just casting
        try:
            # Check current type
            await conn.execute(text("ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768);"))
            print("Altered embedding column to vector(768).")
        except Exception as e:
            print(f"Note: Could not alter column (might already be 768 or has data mismatch): {e}")

        # Create index
        try:
            await conn.execute(text("CREATE INDEX IF NOT EXISTS idx_doc_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);"))
            print("Created HNSW index successfully.")
        except Exception as e:
            print(f"Failed to create HNSW index: {e}")

if __name__ == "__main__":
    asyncio.run(apply_hnsw_index())
