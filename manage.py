#!/usr/bin/env python


import tabulate
import typer
from typing import List, Optional
from typing_extensions import Annotated
from sqlmodel import Session
from sqlmodel.sql.expression import select
from fastapi import Depends
from fastapi.params import Security
from app.models.users import User, UserScopes
from app.auth.security import get_password_hash
from app.db import get_session
from app.main import create_app


app = typer.Typer()

session: Session = next(get_session())


@app.command()
def add_scopes(
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
def list_scopes(username: str) -> None:
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    if not user.scopes:
        print(f"{user.username} has no scopes")
        return
    print(f"{user.username} has scopes {user.scopes}")


@app.command()
def list_routes():
    fastapi_app = create_app()
    headers = ["Path", "Scopes"]
    table = []
    for route in fastapi_app.routes:
        dependencies = getattr(route, "dependencies", [])
        scopes = get_scopes_from_dependencies(dependencies)
        table.append([route.path, scopes])

    print(tabulate.tabulate(table, headers=headers, tablefmt="fancy_grid"))


@app.command()
def add_user(
    username: Annotated[str, typer.Argument()],
    email: Annotated[str, typer.Option()],
    full_name: Annotated[str, typer.Option()],
    password: Annotated[str, typer.Option()],
) -> None:
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    if user:
        print(f"{user.username} already exists")
        return
    user = User(
        username=username,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        email=email,
    )
    session.add(user)
    session.commit()
    print("User has been added")


@app.command()
def update_user(
    username: Annotated[Optional[str], typer.Argument()],
    email: Annotated[Optional[str], typer.Option()] = None,
    full_name: Annotated[Optional[str], typer.Option()] = None,
    password: Annotated[str, typer.Option()] = None,
    disable: Annotated[Optional[bool], typer.Option()] = None,
    enable: Annotated[Optional[bool], typer.Option()] = None,
):
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    if not user:
        print(f"{username} does not exist")
    user.full_name = full_name or user.full_name
    user.email = email or user.email
    if disable:
        user.disabled = True
    elif enable:
        user.disabled = False

    if password:
        user.hashed_password = get_password_hash(password)
    session.add(user)
    session.commit()
    print("User has been updated")


@app.command()
def remove_user(username: Annotated[Optional[str], typer.Argument()]):
    statement = select(User).where(User.username == username)
    user: User = session.exec(statement).first()
    if not user:
        print(f"User {username} does not exist")
        return

    confirmed_username = input("Enter the name of the user to remove: ")
    if username != confirmed_username:
        print(f"{username} does match {confirmed_username}")
        return

    confirm = input(f"Are you sure you want to remove the user {username}?(y/n)")
    if confirm == "y":
        session.delete(user)
        session.commit()
        print("User has been removed")
    else:
        print("User removal operation cancelled")


@app.command()
def list_users():
    users: List[User] = session.execute(select(User)).all()
    headers = ["Username", "Email", "Full Name", "Disabled", "Scopes"]
    table = []
    for user in users:
        user = user[0]
        disabled = "Y" if user.disabled else "N"
        table.append([user.username, user.email, user.full_name, disabled, user.scopes])
    print(tabulate.tabulate(table, headers=headers, tablefmt="fancy_grid"))


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
