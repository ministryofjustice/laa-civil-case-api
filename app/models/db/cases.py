from sqlalchemy import Column, String

from app.db.database import Base


class Cases(Base):
    __tablename__ = "cases"

    id = Column(String, primary_key=True, unique=True,)
    category = Column(String)
    time = Column(String)