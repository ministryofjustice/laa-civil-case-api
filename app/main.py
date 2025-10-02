from fastapi import FastAPI
from .routers import case_information, security, mock_data
from .config.docs import config as docs_config
from fastapi_versionizer.versionizer import Versionizer


def create_app() -> FastAPI:
    app = FastAPI(**docs_config)
    app.include_router(case_information.router)
    app.include_router(security.router)
    app.include_router(mock_data.router)

    Versionizer(
        app=app,
        prefix_format="/v{major}",
        semantic_version_format="{major}",
        latest_prefix="/latest",
        sort_routes=True,
    ).versionize()
    return app
