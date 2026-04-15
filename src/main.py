from fastapi import FastAPI

from src.api.first_api.user_api import router as courses_api_router

app = FastAPI()

app.include_router(courses_api_router)

from src import api