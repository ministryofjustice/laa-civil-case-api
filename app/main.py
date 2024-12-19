from fastapi import FastAPI
from .routers import case_information, security
from .config.docs import config as docs_config
from app.versioning import VersionedFastAPI


def create_app() -> FastAPI:
    app = VersionedFastAPI(**docs_config)

    routers = [case_information.router, security.router]

    app.add_versioned_routes(routers)

    return app
