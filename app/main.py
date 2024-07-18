from fastapi import FastAPI
from .routers import case_information
import os

cwd = os.getcwd()
os.chdir("./app")


def create_app():
    app = FastAPI()
    app.include_router(case_information.router)
    return app


case_api = create_app()
