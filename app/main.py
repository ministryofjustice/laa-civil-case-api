from fastapi import FastAPI, HTTPException
from typing import Optional
from .routers import case_information
from .db.database import SessionLocal, engine
from .models.db import cases
import os

cwd = os.getcwd()
os.chdir("./app")

cases.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_app():
    app = FastAPI()
    app.include_router(case_information.router)
    return app


case_api = create_app()