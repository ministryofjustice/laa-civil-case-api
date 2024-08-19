from typing import Union
from sqlmodel import Field, SQLModel


class Token(SQLModel):
    access_token: str
    token_type: str

class TokenData(SQLModel):
    username: Union[str, None] = None

class Users(SQLModel, table=True):
    username: str = Field(primary_key=True)
    hashed_password: Union[str, None] = None
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

