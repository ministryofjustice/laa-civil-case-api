from fastapi import FastAPI, Depends, HTTPException, status
from .routers import case_information
from .config.docs import config as docs_config
from .auth.security import create_access_token, get_current_user
from fastapi.security import OAuth2PasswordRequestForm
from .auth.models import User, Token
from .auth.security import authenticate_user
from datetime import timedelta


def create_app():
    app = FastAPI(**docs_config)
    app.include_router(case_information.router)

    # Defines the token endpoint
    @app.post("/token", response_model=Token)
    async def login(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=30)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    @app.get("/users/me", response_model=User)
    async def read_users_me(current_user: User = Depends(get_current_user)):
        return current_user

    return app
