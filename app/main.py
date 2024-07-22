from fastapi import FastAPI
from .routers import case_information
from .config import config


def create_app():
    app = FastAPI(**config)
    app.include_router(case_information.router)
    return app
