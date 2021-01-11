from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import Optional
from .user_logic import UserLogic
from .crypto_logic import CryptoLogic
from ..models import Token, TokenData, User, UserInDB
from ..dependencies import AuthScheme
import os
from jose import JWTError, jwt


class AuthLogic:
    oauth2_scheme = AuthScheme.oauth2_scheme
    AUTH_SECRET_KEY = os.environ['AUTH_SECRET_KEY']
    AUTH_ALGORITHM = os.environ['AUTH_ALGORITHM']
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['AUTH_ACCESS_TOKEN_EXPIRE_MINUTES'])

    # def get_user(username: str, user_logic: UserLogic = Depends(UserLogic), ):
    #     return user_logic.get_user_by_username(username)
    #
    # def authenticate_user(username: str, client_hash: str, user_logic: UserLogic = Depends(UserLogic)):
    #     user = get_user(user_logic, username)
    #     if not user:
    #         return False
    #     if not verify_password(client_hash, user.password_hash):
    #         return False
    #     return user

    fake_users_db = {
        "johndoe": {
            "username": "johndoe",
            "full_name": "John Doe",
            "email": "johndoe@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "enabled": True,
        },
        "janedoe": {
            "username": "janedoe",
            "full_name": "Jane Doe",
            "email": "janedoe@example.com",
            "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
            "enabled": False,
        }
    }

    ## Gets the user from the database
    def get_user(db, username: str):
        if username in db:
            user_dict = db[username]

            ## This needs to be UserInDB
            return UserInDB(**user_dict)

    ## Validates that username and password correspond to a valid user
    ## Returns user on success, errors otherwise
    def authenticate_user(db, username: str, password: str):
        user = AuthLogic.get_user(db, username)

        if not user:
            return False
        if not user.enabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        if not CryptoLogic.verify_password(password, user.hashed_password):
            return False
        return user

    ## Returns the user specified in the Bearer Token
    async def get_current_user_from_bearer_token(token: str = Depends(oauth2_scheme)):
        credentials_exception = HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate" : "Bearer"},
        )

        try:
            payload = jwt.decode(token, AuthLogic.AUTH_SECRET_KEY, algorithms=[AuthLogic.AUTH_ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)

        except JWTError:
            raise credentials_exception

        user = AuthLogic.get_user(AuthLogic.fake_users_db, username=token_data.username)
        if user is None:
            raise credentials_exception
        return user

        if not user:
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    ## Returns the active user authenticated in the session. A disabled
    ## user will return a 400 error
    async def get_current_active_user_from_bearer_token(current_user: User = Depends(get_current_user_from_bearer_token)):
        if not current_user.enabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user

    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({ "exp" : expire })
        encoded_jwt = jwt.encode(to_encode, AuthLogic.AUTH_SECRET_KEY, algorithm=AuthLogic.AUTH_ALGORITHM)
        return encoded_jwt
