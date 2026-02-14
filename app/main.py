from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base


app = FastAPI(title=settings.APP_NAME)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
