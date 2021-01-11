from fastapi import Depends, APIRouter, HTTPException
from ..bin import AuthLogic
from ..models import User

router = APIRouter(
    prefix='/me',
    tags=["me"]
)

@router.get(
    '/',
    response_model=User,
    summary="Get information about the user authenticated in the session."
)
async def read_users_me(current_user: User = Depends(AuthLogic.get_current_active_user_from_bearer_token)):
    return current_user
