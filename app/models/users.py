from typing import Union
from sqlmodel import Field, SQLModel

'''
Declares the JWT token, token type will reference
bearer and the access token is generated per user
encoding via the secret key and HS256
'''
class Token(SQLModel):
    access_token: str
    token_type: str

'''
TokenData links the JWT token to the username
'''
class TokenData(SQLModel):
    username: Union[str, None] = None

class Users(SQLModel, table=True):
    username: str = Field(primary_key=True)
    hashed_password: Union[str, None] = None
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None

