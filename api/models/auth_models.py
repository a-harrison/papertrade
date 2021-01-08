from typing import Optional
from pydantic import BaseModel
from fastapi import Depends

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
