from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth.security import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES
from ..models.users import Token
from app.db import get_session

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


"""
This endpoint accepts a username and password, authenticates the user, and returns a JSON Web Token (JWT) if the credentials are valid. This JWT is signed and will expire after 30 minutes.
This token can then be used to authenticate subsequent requests.

Args:
    form_data (OAuth2PasswordRequestForm): The form data containing the username and password.

Returns:
    Token: An JWT containing the access token and its type.

Raises:
    HTTPException: If authentication fails, an HTTP 401 Unauthorised error is raised with
                   a message indicating incorrect username or password.
"""
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")
