import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

engine = create_async_engine('postgresql+asyncpg://postgres.krmlhgxltwjbeeuvbxbu:NELXIYax7KwxPWBq@aws-1-ap-northeast-2.pooler.supabase.com:5432/postgres')

async def run():
    async with engine.begin() as conn:
        try:
            await conn.execute(text('ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(768);'))
            print("Successfully altered table!")
        except Exception as e:
            print("Error:", e)

asyncio.run(run())
