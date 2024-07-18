# One line of FastAPI imports here later 👈
from sqlmodel import create_engine
import os

cwd = os.getcwd()

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
