from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import public_router, router
from .core.rate_limit import RateLimitMiddleware
from .db.session import init_db
from .graph.client import get_graph
from .rag.store import get_store


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    get_store()   # warm the FAISS index
    get_graph()   # connect to Neo4j (or fall back to in-memory graph)
    yield


app = FastAPI(
    title="Autonomous Fraud Investigation System",
    description="Agentic RAG + Graph ML fraud investigation backend",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware, limit=240, window_seconds=60)

app.include_router(public_router)
app.include_router(router)
