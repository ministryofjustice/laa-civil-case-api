from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from ..auth.security import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_active_user
from ..models.users import Users, Token
from app.db import get_session

router = APIRouter(
    responses={404: {"description": "Not found"}},
)


'''
The below function generates a JWT for a user who has
provided a username and password. This JWT is unique
and signed with an expiry time.
'''
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(get_session(), form_data.username, form_data.password)
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
