import typer
from typing import List
from typing_extensions import Annotated
from sqlmodel import Session
from sqlmodel.sql.expression import select
from app.models.users import User, UserScopes
from app.db import get_session

app = typer.Typer()

session: Session = next(get_session())


@app.command()
def user_scopes_add(
    username: str, scope: Annotated[List[UserScopes], typer.Option()]
) -> None:
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    print(
        f"Replacing user {user.username} current scopes {user.scopes} with new scopes {scope}..."
    )
    user.scopes = scope
    session.add(user)
    session.commit()
    print("Done")


@app.command()
def user_scopes_list(username: str) -> None:
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    if not user.scopes:
        print(f"{user.username} has no scopes")
        return
    print(f"{user.username} has scopes {user.scopes}")


if __name__ == "__main__":
    app()
