from fastapi import FastAPI

from src.api import router
from src.clickhouse.client import get_client
from src.clickhouse.migrations import run_migrations

app = FastAPI(title="Auction Stats ClickHouse")

app.include_router(router.router, prefix="/api/v1")


@app.on_event("startup")
def startup():
    run_migrations()


@app.get("/health")
def health():
    try:
        client = get_client()
        client.command("SELECT 1")
        return {"status": "ok"}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}
