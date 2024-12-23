from fastapi import FastAPI
from .routers import case_information, security
from .config.docs import config as docs_config
from app.versioning import VersionedFastAPI


def create_app() -> FastAPI:
    app = VersionedFastAPI(**docs_config)

    versioned_routers = [case_information.router]

    app.add_versioned_routes(versioned_routers)
    app.include_router(security.router)

    return app
