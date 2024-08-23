from typing import Union, Annotated
from datetime import timezone, timedelta, datetime

from passlib.context import CryptContext
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends, status
from app.models.users import Users, TokenData, Token
from app.config import Config
from app.db import get_session
from sqlmodel import Session

import logging

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = Config.SECRET_KEY

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    This function runs bcrypt salting and hashing via passlib.

    Args:
        password: Password data as a string.

    Returns:
        password: Returns a hashed and salted password using
        passlib bcrypt.
    """
    return pwd_context.hash(password)

def get_user(session, username: str):
    user = session.get(Users, username)

    return user

def authenticate_user(session, username: str, password: str) -> str | Users | bool:
    """
    This function returns the user if they are authenticated against their
    hashed password and exist in the database. Used in service login.

    Args:
        username: Username data as a string
        password: Password data as a string

    Returns:
        user: A string that contains the user information to be used
        to create the access token
        False: If user does not exist or if the verify password function
        cannot match the current password with the hashed user password
    """
    user = get_user(session, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None) -> Token:
    """
    Creates the JWT access token with an expiry time.

    Args:
        data: A dictionary containing the username.
        expires_delta: A timedelta of the expiry time of the token.

    Returns:
        encoded_jwt: Returns the fully encoded JWT with expiry time.
    """
    """
    Data.copy is used to avoid updating the original data dictionary with
    the expiry field to ensure it can still be read as a standalone object.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    """
    Checks the current user token to return a user.

    Args:
        token: Uses the oauth2 scheme to get the current JWT.

    Returns:
        user: Returns the current user object by verifying against the JWT.

    Raises:
        HTTP_Exception: If authentication fails, a HTTP 401 Unauthorised error is
        raised with a message indicating that the credentials could not be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        logging.warning(f"Invalid Token Authorisation on token {token}")
        raise credentials_exception
    user = get_user(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[Users, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User Disabled",
    )
    return current_user