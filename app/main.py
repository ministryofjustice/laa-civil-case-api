from fastapi import FastAPI, HTTPException
from typing import Optional
from .routers import case_information
from .models import cases
import os

cwd = os.getcwd()
os.chdir("./app")


def create_app():
    app = FastAPI()
    app.include_router(case_information.router)
    return app


case_api = create_app()
