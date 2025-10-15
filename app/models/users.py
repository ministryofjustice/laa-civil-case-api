from sqlmodel import Field, SQLModel, JSON
from enum import Enum
from typing import List


class UserScopes(str, Enum):
    READ = "read"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    @classmethod
    def as_list(cls):
        # Iterate over the values only
        return [member.value for member in cls]

    @classmethod
    def as_dict(cls) -> dict:
        return {member.name: member.value for member in cls}


class Token(SQLModel):
    """JSON Web Token (JWT) provided to the user after authentication."""

    access_token: str
    token_type: str


class TokenData(SQLModel):
    """TokenData links the JWT token to the username"""

    username: str | None = None


class User(SQLModel, table=True):
    """
    Users are required to be authenticated to use some functionality of the API.
    Disabled users are unable to authenticate to receive a token.
    """

    __tablename__ = "users"

    username: str = Field(primary_key=True)
    hashed_password: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = Field(default=False)
    scopes: List[UserScopes] = Field(sa_type=JSON, default=[], nullable=True)
