from sqlmodel import Field, SQLModel


class Token(SQLModel):
    """JSON Web Token (JWT) provided to the user after authentication."""

    access_token: str
    token_type: str


class Users(SQLModel, table=True):
    """
    Users are required to be authenticated to use some functionality of the API.
    Disabled users are unable to authenticate to receive a token.
    """

    username: str = Field(primary_key=True)
    hashed_password: str | None = None
    email: str | None = None
    full_name: str | None = None
    disabled: bool = Field(default=False)
