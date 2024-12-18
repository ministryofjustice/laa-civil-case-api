from fastapi import FastAPI
from .config.docs import config as docs_config
from .routers.v1 import router as v1_router


def create_app() -> FastAPI:
    app = FastAPI(**docs_config)
    app.include_router(v1_router)

    return app
