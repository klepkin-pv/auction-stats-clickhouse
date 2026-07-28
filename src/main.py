from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api import router
from src.cache import invalidate_stats
from src.clickhouse.client import get_client
from src.clickhouse.migrations import run_migrations


@asynccontextmanager
async def lifespan(app: FastAPI):
    run_migrations()
    invalidate_stats()
    yield


app = FastAPI(title="Auction Stats ClickHouse", lifespan=lifespan)

app.include_router(router.router, prefix="/api/v1")


@app.get("/health")
def health():
    try:
        client = get_client()
        client.command("SELECT 1")
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
