from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from api.api import router
from api.config import settings
from api.registry import _embed_query

from mes_agent import service as mes_service

@asynccontextmanager
async def lifespan(app):
    await mes_service.init()
    yield

app = FastAPI(title="chat backend", lifespan=lifespan)
print("Loading vector index and embedding model...")
_embed_query("test")  # load up the embedding model

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    )

app.include_router(router)