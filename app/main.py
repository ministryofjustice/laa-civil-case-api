from fastapi import FastAPI, APIRouter
from .routers.v1 import case_information as case_information_v1, security as security_v1
from .config.docs import config as docs_config


def v1_router():
    router = APIRouter(prefix="/v1")
    router.include_router(case_information_v1.router)
    router.include_router(security_v1.router)
    return router


def v2_router():
    router = APIRouter(prefix="/v2")
    router.include_router(case_information_v1.router)
    return router


def create_app() -> FastAPI:
    app = FastAPI(**docs_config)
    app.include_router(v1_router())

    return app
