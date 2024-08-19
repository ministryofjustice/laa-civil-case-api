from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, status
from .routers import case_information
from .config.docs import config as docs_config
from .auth.security import create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from .auth.security import User, Token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def create_app():
    app = FastAPI(**docs_config)
    app.include_router(case_information.router)

    # Defines the token endpoint
    @app.post("/token")
    async def login_for_access_token(
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> Token:
        user = authenticate_user(fake_users_db, form_data.username, form_data.password)
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
    
    @app.get("/users/me", response_model=User)
    async def read_users_me(current_user: User = Depends(get_current_user)):
        return current_user

    return app
