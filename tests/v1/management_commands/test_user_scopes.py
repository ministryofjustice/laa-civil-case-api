from typer.testing import CliRunner
from sqlmodel import Session
from app.models.users import User, UserScopes
from app.auth.security import get_password_hash
from manage import app as management_app, init_session


def test_user_scopes_add(session: Session):
    user = User(
        **{
            "username": "test_user",
            "hashed_password": get_password_hash("password123"),
            "fullname": "Test User",
            "email": "test.user@digital.justice.gov.uk",
        }
    )
    session.add(user)
    session.commit()
    assert user.scopes == []
    init_session(management_app, session)
    runner = CliRunner()
    result = runner.invoke(
        management_app,
        ["set-user-scopes", "--scope", "read", "--scope", "update", user.username],
    )
    expected_msg = f"Replacing user {user.username} current scopes [] with new scopes ['read', 'update']...done"
    assert expected_msg in result.stdout
    assert user.scopes == [UserScopes("read"), UserScopes("update")]


def test_user_scopes_replace(session: Session):
    user = User(
        **{
            "username": "test_user",
            "hashed_password": get_password_hash("password123"),
            "fullname": "Test User",
            "email": "test.user@digital.justice.gov.uk",
            "scopes": ["read", "update"],
        }
    )
    session.add(user)
    session.commit()
    assert len(user.scopes) == 2
    init_session(management_app, session)
    runner = CliRunner()
    result = runner.invoke(
        management_app, ["set-user-scopes", "--scope", "create", user.username]
    )
    expected_msg = f"Replacing user {user.username} current scopes ['read', 'update'] with new scopes ['create']...done"
    assert expected_msg in result.stdout
    assert user.scopes == [UserScopes("create")]
