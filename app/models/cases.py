from sqlmodel import Field, SQLModel
from datetime import datetime
from .categories import Categories


class BaseCase(SQLModel):
    category: Categories = Field(index=True)
    name: str


class Case(BaseCase, table=True):
    id: int = Field(default=None, primary_key=True)
    time: datetime


class CaseRequest(BaseCase):
    pass


class CaseLookup(SQLModel):
    id: int
