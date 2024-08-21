from app.db import get_session
from app.models.users import Users
from app.auth.security import get_password_hash
import logging

def add_users(users_list_dict: dict):
    """
    This function creates new users in the spun up local database

    Args:
        users_list_dict: Should contain a list of dictionary 
        usernames and plain text passwords for users

    Logs:
        Logger warning: If username already exists will raise a
        warning and ignore adding this user. It was also raise
        a warning if there is a missing username/password.
    """
    with next(get_session()) as session:
        for user_info in users_list_dict:
            username = user_info.get('username')
            password = user_info.get('password')

            if not username or not password:
                logging.warning(f"Skipping user with missing username or password: {user_info}")
                continue

            # Check if the username already exists
            existing_user = session.get(Users, username)
            if existing_user:
                logging.warning(f"User with username '{username}' already exists.")
                continue

            password = get_password_hash(password)
            new_user = Users(username=username, hashed_password=password)
            session.add(new_user)

        session.commit()

users_to_add = [
        {'username': 'cla_admin', 'password': 'cla_admin'},
        {'username': 'janedoe', 'password': 'password'}
]

add_users(users_to_add)