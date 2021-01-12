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

    async def get_user(user_logic: UserLogic, username: str):
        return await user_logic.get_user_by_username(username)

    async def authenticate_user(user_logic: UserLogic, username: str, password: str):
        user = await AuthLogic.get_user(user_logic, username)
        print(user)

        if not user:
            return False
        if not user['enabled']:
            raise HTTPException(status_code=400, detail="Inactive user")
        if not CryptoLogic.verify_password(password, user['password_hash']):
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

        user = AuthLogic.get_user(user_logic, username=token_data.username)
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

    ## Creates access token with specified expiration time
    async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({ "exp" : expire })
        encoded_jwt = jwt.encode(to_encode, AuthLogic.AUTH_SECRET_KEY, algorithm=AuthLogic.AUTH_ALGORITHM)
        return encoded_jwt
