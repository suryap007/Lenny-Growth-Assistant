import asyncio
from sqlalchemy import text
from app.db.session import engine, Base
from app.db.models import User, ChatSession, Message, Document, DocumentChunk

async def init_db():
    async with engine.begin() as conn:
        print("Creating pgvector extension if not exists...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        print("Creating tables...")
        await conn.run_sync(Base.metadata.create_all)
    print("Database initialization complete.")

if __name__ == "__main__":
    asyncio.run(init_db())
