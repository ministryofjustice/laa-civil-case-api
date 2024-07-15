from pydantic import BaseModel
from ..categories import Categories

class Case(BaseModel):
    category: Categories