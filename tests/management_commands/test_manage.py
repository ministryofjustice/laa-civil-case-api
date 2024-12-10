from typer.testing import CliRunner
from sqlmodel import Session
from sqlmodel.sql.expression import select
from app.models.users import User
from app.auth.security import get_password_hash
from manage import app as management_app, init_session

runner = CliRunner()


test_user_details = {
    "username": "test_user",
    "password": "password123",
    "fullname": "Test User",
    "email": "test.user@digital.justice.gov.uk",
}


def test_add_user_command(session: Session) -> None:
    init_session(management_app, session)
    statement = select(User).where(User.username == test_user_details["username"])
    assert session.exec(statement).first() is None

    result = runner.invoke(
        management_app,
        [
            "add-user",
            test_user_details["username"],
            "--email",
            test_user_details["email"],
            "--password",
            test_user_details["password"],
            "--full-name",
            test_user_details["fullname"],
        ],
    )
    assert "User has been added" in result.stdout

    statement = select(User).where(User.username == test_user_details["username"])
    user = session.exec(statement).first()
    assert user.username == test_user_details["username"]


def test_update_user_command(session: Session) -> None:
    init_session(management_app, session)
    user_details = test_user_details.copy()
    user_details["hashed_password"] = get_password_hash(user_details["password"])
    user = User(**user_details)
    session.add(user)
    session.commit()

    result = runner.invoke(
        management_app,
        [
            "update-user",
            user_details["username"],
            "--email",
            "test.user.updated@digital.justice.gov.uk",
            "--password",
            "updatedpassword",
            "--full-name",
            "Test User Updated",
            "--disable",
        ],
    )
    assert "User has been updated" in result.stdout
    session.refresh(user)
    assert user.email == "test.user.updated@digital.justice.gov.uk"
    assert user.hashed_password != user_details["hashed_password"]
    assert user.full_name == "Test User Updated"
    assert user.disabled

    # Enable disabled user
    result = runner.invoke(
        management_app, ["update-user", user_details["username"], "--enable"]
    )
    session.refresh(user)
    assert not user.disabled


def test_add_user_existing_command(session: Session) -> None:
    init_session(management_app, session)
    user_details = test_user_details.copy()
    user_details["hashed_password"] = get_password_hash(user_details["password"])
    user = User(**user_details)
    session.add(user)
    session.commit()

    result = runner.invoke(
        management_app,
        [
            "add-user",
            user_details["username"],
            "--email",
            user_details["email"],
            "--password",
            user_details["password"],
            "--full-name",
            user_details["fullname"],
        ],
    )
    assert f"{user_details['username']} already exists" in result.stdout


def test_delete_user_command(session: Session, monkeypatch) -> None:
    init_session(management_app, session)
    user_details = test_user_details.copy()
    user_details["hashed_password"] = get_password_hash(user_details["password"])
    user = User(**user_details)
    session.add(user)
    session.commit()
    statement = select(User).where(User.username == user_details["username"])
    assert len(session.exec(statement).all()) == 1

    # monkeypatch the "input" function, so that it returns our test username.
    inputs = {
        "Enter the name of the user to remove: ": user_details["username"],
        f"Are you sure you want to remove the user {user_details['username']}?(y/n): ": "y",
    }

    def get_inputs(prompt: str) -> str:
        return inputs.get(prompt)

    monkeypatch.setattr("builtins.input", get_inputs)
    result = runner.invoke(management_app, ["delete-user", user_details["username"]])
    assert "User has been removed" in result.stdout
    assert len(session.exec(statement).all()) == 0


def test_delete_user_cancel_command(session: Session, monkeypatch) -> None:
    init_session(management_app, session)
    user_details = test_user_details.copy()
    user_details["hashed_password"] = get_password_hash(user_details["password"])
    user = User(**user_details)
    session.add(user)
    session.commit()

    # monkeypatch the "input" function, so that it returns our test username.
    inputs = {
        "Enter the name of the user to remove: ": user_details["username"],
        f"Are you sure you want to remove the user {user_details['username']}?(y/n): ": "n",
    }

    def get_inputs(prompt: str) -> str:
        return inputs.get(prompt)

    monkeypatch.setattr("builtins.input", get_inputs)
    result = runner.invoke(management_app, ["delete-user", user_details["username"]])
    assert "User removal operation cancelled" in result.stdout
    statement = select(User).where(User.username == user_details["username"])
    assert len(session.exec(statement).all()) == 1
