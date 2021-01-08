from fastapi import Depends, APIRouter, HTTPException
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from ..bin import UserLogic
from ..models import UserResponseModel, UserCreationModel, User, UserException

router = APIRouter(
    prefix='/users',
    tags=["users"]
)

# TODO: Needs auth
@router.get(
    "/{user_id}",
    response_model=UserResponseModel,
    summary="Get a single user by _id"
)
async def read_user(
    user_id: str,
    user_logic: UserLogic = Depends(UserLogic)
):
    user = await user_logic.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    else:
        return user

@router.post(
    "/",
    summary="Create a user"
)
async def create_user(
    user: UserCreationModel,
    user_logic: UserLogic = Depends(UserLogic)
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
    user_logic: UserLogic = Depends(UserLogic)
):
    try:
        result = await user_logic.delete_user_by_id(user_id)
        return result
    except UserException as user_exception:
        raise HTTPException(status_code=404, detail=user_exception.message)
# 
# @router.get(
#     '/me',
#     summary="Get information about the user authenticated in the session."
# )
# async def read_users_me(current_user: User = Depends(get_current_user)):
#     return current_user
