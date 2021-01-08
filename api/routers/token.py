from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from ..bin import AuthLogic

router = APIRouter(
    tags=["token"]
)

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = AuthLogic.authenticate_user(AuthLogic.fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate" : "Bearer"},
        )
    access_token_expires = timedelta(minutes=AuthLogic.AUTH_ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = AuthLogic.create_access_token(
        data = { "sub" : user.username }, expires_delta=access_token_expires
    )
    return {"access_token" : access_token, "token_type": "bearer"}
