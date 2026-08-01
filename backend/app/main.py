from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import router as api_router
from app.db.session import engine, Base
import os
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Depending on alembic for real migrations, but we can also ensure tables exist
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Lenny Growth Assistant", lifespan=lifespan)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
