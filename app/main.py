from fastapi import FastAPI
from .routers import case_information
import os


def create_app():
    app = FastAPI()
    app.include_router(case_information.router)
    return app

if __name__ == "__main__":
    cwd = os.getcwd()
    os.chdir("./app")