from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.api.first_api.user_api import router as clients_api_router
from src.web.routes import router as web_router

BASE_DIR = Path(__file__).resolve().parents[1]

app = FastAPI(title='ЦФП «Динамика»')

app.mount('/static', StaticFiles(directory=str(BASE_DIR / 'static')), name='static')

app.include_router(web_router)
app.include_router(clients_api_router)
