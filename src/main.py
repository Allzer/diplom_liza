from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from config import SECRET
from src.api.first_api.user_api import router as clients_api_router
from src.web.auth_routes import router as auth_router
from src.web.handlers import register_exception_handlers
from src.web.routes import router as web_router
from src.web.templates_ctx import templates

BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(title='ЦФП «Динамика»')

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET or 'change-me-in-env-secret-key',
    session_cookie='cfp_session',
    max_age=60 * 60 * 24 * 14,
)

app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

register_exception_handlers(app, templates)

app.include_router(web_router)
app.include_router(auth_router)
app.include_router(clients_api_router)
