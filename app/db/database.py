# One line of FastAPI imports here later 👈
from sqlmodel import Field, Session, SQLModel, create_engine, select
from app.models.cases import Case
from datetime import datetime
import os

cwd = os.getcwd()

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
