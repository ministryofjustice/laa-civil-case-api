from fastapi import FastAPI
from .routers import case_information
from .config.docs import config as docs_config


def create_app():
    app = FastAPI(**docs_config)
    app.include_router(case_information.router)
    return app
