# One line of FastAPI imports here later 👈
from sqlmodel import Field, SQLModel
from datetime import datetime

class RequestCase(SQLModel):
    category: str = Field(index=True)


class Case(RequestCase, table=True):
    id: str | None = Field(default=None, primary_key=True)
    time: datetime