from app.db import get_session
from app.models.users import Users
from sqlmodel import select
from app.auth.security import get_password_hash
from logging import Logger

def add_users(users_list_dict: dict):
    """
    This function creates new users in the spun up local database

    Args:
        users_list_dict: Should contain a list of dictionary 
        usernames and plain text passwords for users

    Raises:
        Logger warning: If username already exists will raise a
        warning and ignore adding this user.
    """
    with next(get_session()) as session:
        for user_info in users_list_dict:
            username = user_info.get('username')
            password = user_info.get('password')

            if not username or not password:
                Logger.warning(f"Skipping user with missing username or password: {user_info}")
                continue

            # Check if the username already exists
            existing_user = session.get(Users, username)
            if existing_user:
                print(f"User with username '{username}' already exists.")
                continue

            password = get_password_hash(password)
            new_user = Users(username=username, hashed_password=password)
            session.add(new_user)

        session.commit()

users_to_add = [
        {'username': 'johndoe', 'password': 'password'},
        {'username': 'janedoe', 'password': 'password'}
]

add_users(users_to_add)