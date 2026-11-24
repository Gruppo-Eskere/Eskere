import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy.engine import Engine

from app.config import get_settings
from app.database import Base, engine as default_engine
from app.routers import admin, auth, impianti, segnalazioni

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parent


def create_app(database_engine: Engine | None = None) -> FastAPI:
    settings = get_settings()
    @asynccontextmanager
    async def lifespan(application: FastAPI):
        Base.metadata.create_all(bind=application.state.engine)
        yield

    application = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
    application.state.engine = database_engine or default_engine
    application.state.templates = Jinja2Templates(directory=str(APP_DIR / "templates"))
    application.state.logger = logging.getLogger("benzina_chiara")
    application.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        session_cookie="benzina_chiara_session",
        same_site="lax",
        https_only=settings.cookie_secure,
        max_age=60 * 60 * 12,
    )
    application.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")

    application.include_router(auth.router)
    application.include_router(impianti.router)
    application.include_router(segnalazioni.router)
    application.include_router(admin.router)
    return application


app = create_app()
