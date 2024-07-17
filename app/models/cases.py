# One line of FastAPI imports here later 👈
from sqlmodel import Field, SQLModel
from datetime import datetime

class BaseCase(SQLModel):
    category: str = Field(index=True)
    name: str

class Case(BaseCase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    time: datetime

class CaseCreate(BaseCase):
    pass

class CaseRead(SQLModel):
    id: int