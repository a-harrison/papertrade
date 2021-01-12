from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Class representing required fields necessary to create a user
# We use a separate model from 'UserModel' to prevent the client from setting
# the password hash or the salt, which must be created server-side
class UserCreationModel(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    enabled: Optional[bool] = None
    client_hash: str        # Addition to UserBaseModel

# Class representing only fields that should be returned when accessing a user
class UserResponseModel(BaseModel):
    _id: str                # Addition to UserBaseModel
    username: str
    email: str
    full_name: Optional[str] = None
    enabled: bool
    creation_date: datetime # Addition to UserBaseModel

# Model representing all fields of the User class
class User(BaseModel):
    _id: str                # Addition to UserBaseModel
    username: str
    email: str
    full_name: Optional[str] = None
    enabled: Optional[bool] = False
    creation_date: Optional[datetime] = None # Addition to UserBaseModel

class UserInDB(User):
    password_hash: str
