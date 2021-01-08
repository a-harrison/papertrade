from passlib.context import CryptContext
from fastapi import Depends
from .user_logic import UserLogic
import os

class AuthLogic:
    AUTH_SECRET_KEY = os.environ['AUTH_SECRET_KEY']
    AUTH_ALGORITHM = os.environ['AUTH_ALGORITHM']
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ['AUTH_ACCESS_TOKEN_EXPIRE_MINUTES']

    def get_user(username: str, user_logic: UserLogic = Depends(UserLogic), ):
        return user_logic.get_user_by_username(username)

    def authenticate_user(username: str, client_hash: str, user_logic: UserLogic = Depends(UserLogic)):
        user = get_user(user_logic, username)
        if not user:
            return False
        if not verify_password(client_hash, user.password_hash):
            return False
        return user
