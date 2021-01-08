from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from .routers import users
from .bin import UserLogic
from .dependencies import DBHandlerInitializer, DBHandler, AuthScheme
import os

from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .models import Token, TokenData

from .bin import CryptoLogic
from fastapi.security import OAuth2PasswordRequestForm

app = FastAPI()
oauth2_scheme = AuthScheme.oauth2_scheme
MONGODB_URI = os.environ['MONGODB_URI']
AUTH_SECRET_KEY = os.environ['AUTH_SECRET_KEY']
AUTH_ALGORITHM = os.environ['AUTH_ALGORITHM']
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['AUTH_ACCESS_TOKEN_EXPIRE_MINUTES'])

async def get_db_handler():
    return await DBHandler.get_db_handler()

@app.on_event("startup")
def startup_event():
    ## TODO: Validate that all required environment variables are defined.
    MONGODB_URI = os.environ['MONGODB_URI']
    AUTH_SECRET_KEY = os.environ['AUTH_SECRET_KEY']
    AUTH_ALGORITHM = os.environ['AUTH_ALGORITHM']
    AUTH_ACCESS_TOKEN_EXPIRE_MINUTES = os.environ['AUTH_ACCESS_TOKEN_EXPIRE_MINUTES']

    if any(config_var is None for config_var in [MONGODB_URI, AUTH_SECRET_KEY, AUTH_ALGORITHM, AUTH_ACCESS_TOKEN_EXPIRE_MINUTES]):
        print("A required configuration variable is not defined.")
        print("Aborting startup...")
    else:
        print("Starting up...")

        # Client connections are shared across object instances
        # so creating it here will allow other objects to access the connection
        db_handler_initiazer = DBHandlerInitializer(os.environ['MONGODB_URI'])

@app.on_event("shutdown")
def shutdown_event():
    print("Shutting down...")

@app.get("/")
async def read_main():
    return {"message" : "Hello World"}

##################################################################

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
    }
}

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]

        ## This needs to be UserInDB
        return UserInDB(**user_dict)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({ "exp" : expire })
    encoded_jwt = jwt.encode(to_encode, AUTH_SECRET_KEY, algorithm=AUTH_ALGORITHM)
    return encoded_jwt

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    hashed_password: str

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate" : "Bearer"},
    )

    try:
        payload = jwt.decode(token, AUTH_SECRET_KEY, algorithms=[AUTH_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)

    except JWTError:
        raise credentials_exception

    user = get_user(fake_users_db, username=token_data.username)
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

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not CryptoLogic.verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get(
    "/users/me",
    response_model=User
)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expires = timedelta(minutes=AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data = { "sub" : user.username }, expires_delta=access_token_expires
    )
    return {"access_token" : access_token, "token_type": "bearer"}

app.include_router(users.router)
