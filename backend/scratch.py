import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test():
    engine = create_async_engine('postgresql+asyncpg://postgres.krmlhgxltwjbeeuvbxbu:NELXIYax7KwxPWBq@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres')
    async with engine.begin() as conn:
        res = await conn.execute(text('SELECT * FROM chat_sessions'))
        print(res.fetchall())

if __name__ == "__main__":
    asyncio.run(test())
