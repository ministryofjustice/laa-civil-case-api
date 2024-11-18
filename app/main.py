from fastapi import FastAPI
from .routers import case_information, security
from .config.docs import config as docs_config


def create_app(*args, **kwargs):
    app = FastAPI(*args, **kwargs, **docs_config)
    app.include_router(case_information.router)
    app.include_router(security.router)

    return app
