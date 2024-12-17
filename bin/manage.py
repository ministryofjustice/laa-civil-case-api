#!/usr/bin/env python

import json
import typer
from typing import List
from typing_extensions import Annotated
from sqlmodel import Session
from sqlmodel.sql.expression import select
from fastapi import Depends
from fastapi.params import Security
from ..app.models.users import User, UserScopes
from ..app.db import get_session
from ..app.main import create_app

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


@app.command()
def routes_list():
    fastapi_app = create_app()
    routes = {}
    for route in fastapi_app.routes:
        dependencies = getattr(route, "dependencies", [])
        routes[route.path] = {"scopes": get_scopes_from_dependencies(dependencies)}

    output = json.dumps(routes, indent=4)
    print(output)


def get_scopes_from_dependencies(dependencies: List[Depends]):
    scopes = []
    for dependency in dependencies:
        if isinstance(dependency, Security):
            items = getattr(dependency, "scopes", [])
            for item in items:
                scopes.append(item)
    return scopes


if __name__ == "__main__":
    app()
