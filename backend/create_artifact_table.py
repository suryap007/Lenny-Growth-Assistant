import asyncio
from app.db.session import engine, Base
from app.db.models import Artifact

async def create_artifact_table():
    async with engine.begin() as conn:
        print("Creating Artifact table if not exists...")
        await conn.run_sync(Base.metadata.create_all)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(create_artifact_table())
