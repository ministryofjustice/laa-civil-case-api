# One line of FastAPI imports here later 👈
from sqlmodel import Field, SQLModel
from datetime import datetime

class Cases(SQLModel, table=True):
    id: str | None = Field(default=None, primary_key=True)
    category: str = Field(index=True)
    time: datetime