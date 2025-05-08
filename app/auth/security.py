from typing import Annotated
from datetime import timezone, timedelta, datetime

from passlib.hash import argon2
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from fastapi import HTTPException, Depends, status, Security
from app.models.users import User, TokenData
from app.config import Config
from app.db import get_session
from sqlmodel import Session

import logging

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = Config.SECRET_KEY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return argon2.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    This function runs argon2 salting and hashing via passlib.

    Args:
        password: Password data as a string.

    Returns:
        password: Returns a hashed and salted password using
        passlib argon2.
    """
    return argon2.hash(password)


def authenticate_user(session, username: str, password: str) -> str | User | bool:
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
    user = session.get(User, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(
    data: dict, scopes: list | None = None, expires_delta: timedelta | None = None
) -> str:
    """
    Creates the JWT access token with an expiry time.

    Args:
        data: A dictionary containing the username.
        scopes: A list of scopes assigned to the user.
        expires_delta: A timedelta of the expiry time of the token.

    Returns:
        encoded_jwt: Returns the fully encoded JWT with expiry time.
    """
    """
    Data.copy is used to avoid updating the original data dictionary with
    the expiry field to ensure it can still be read as a standalone object.
    """
    to_encode = data.copy()
    scopes = scopes or []
    to_encode.update({"scopes": scopes})
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def token_decode(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)],
):
    """
    Checks the current user token to return a user.

    Args:
        security_scopes:  Security scopes user should have access to.
        token: Uses the oauth2 scheme to get the current JWT.
        session: Uses the session object to get the current user.

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

    scopes_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not enough permissions",
        headers={"WWW-Authenticate": f'Bearer scope="{security_scopes.scope_str}"'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_data = TokenData(username=username)
    except InvalidTokenError:
        logging.warning(f"Invalid Token Authorisation on token {token}")
        raise credentials_exception
    user = session.get(User, token_data.username)
    if user is None:
        raise credentials_exception

    if security_scopes.scopes and not user.scopes:
        raise scopes_exception

    for scope in security_scopes.scopes:
        if scope not in user.scopes:
            raise scopes_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Security(get_current_user, scopes=[])],
):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User Disabled",
        )

    return current_user
