import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import NullPool
from app.db.session import DATABASE_URL, Base, get_db
from app.main import app

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(
        DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        }
    )
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with TestingSessionLocal() as session:
        yield session

    app.dependency_overrides.clear()
    await engine.dispose()
