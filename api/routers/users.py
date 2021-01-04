from fastapi import Depends, APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..db import UserLogic
from ..models import UserResponseModel, UserCreationModel, UserException

router = APIRouter(
    prefix='/users',
    tags=["users"]
)

user_logic = None

## Obtains an instance of UserLogic, which is responsible for querying the
## database. This will call a method for obtaining the shared db connection.
async def get_user_logic():
    user_logic = UserLogic()
    return user_logic

class User(BaseModel):
    _id: Optional[str] = None # Will not be defined during user creation
    username: str
    email: str
    client_hash: Optional[str] = None
    hashed_password: Optional[str] = None
    password_salt: str
    enabled: bool
    creation_date: Optional[datetime] = None

UserCreationModel = UserCreationModel

# TODO: Needs auth
@router.get(
    "/{user_id}",
    response_model=UserResponseModel,
    summary="Get a single user by _id"
)
async def read_user(
    user_id: str,
    user_logic: UserLogic = Depends(get_user_logic)
):
    user = await user_logic.get_user_by_id(user_id)
    return user

@router.post(
    "/",
    summary="Create a user"
)
async def create_user(
    user: UserCreationModel ,
    user_logic: UserLogic = Depends(get_user_logic)
):
    try:
        user = await user_logic.create_user(user)
        return user
    except UserException as user_exception:
        raise HTTPException(status_code=409, detail=user_exception.message)

# TODO: Needs auth
@router.delete(
    "/{user_id}",
    summary="Delete a single user by _id"
)
async def delete_user(
    user_id: str,
    user_logic: UserLogic = Depends(get_user_logic)
):
    try:
        result = await user_logic.delete_user_by_id(user_id)
        return result
    except UserException as user_exception:
        raise HTTPException(status_code=404, detail=user_exception.message)
