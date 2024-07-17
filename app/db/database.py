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

def create_db_and_tables():
    if os.path.exists(cwd + '/' + sqlite_file_name):
        os.remove(cwd + '/' + sqlite_file_name)
    SQLModel.metadata.create_all(engine)