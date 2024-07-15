from pydantic import BaseModel
from datetime import datetime

class Case(BaseModel):
    category: str
    id: str
    time: datetime