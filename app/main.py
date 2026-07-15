from fastapi import FastAPI

from app.api import routes
from app.core.config import settings
from app.db.clickhouse import init_db

app = FastAPI(title=settings.app_name)
app.include_router(routes.router)


@app.on_event("startup")
def startup() -> None:
    init_db()
