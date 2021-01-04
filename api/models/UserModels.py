from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Base user class of fields that should be present in all forms of a user
class UserBaseModel(BaseModel):
    username: str
    email: str
    enabled: bool

# Class representing required fields necessary to create a user
class UserCreationModel(UserBaseModel):
    username: str
    email: str
    enabled: bool
    client_hash: str        # Addition to UserBaseModel

# Class representing only fields that should be returned when accessing a user
class UserResponseModel(BaseModel):
    _id: str                # Addition to UserBaseModel
    username: str
    email: str
    enabled: bool
    creation_date: datetime # Addition to UserBaseModel

# Model representing all fields of the User class
class UserModel(UserResponseModel):
    _id: str                # Addition to UserBaseModel
    username: str
    email: str
    enabled: bool
    creation_date: datetime # Addition to UserBaseModel
    hashed_password: str    # Addition to UserResponseModel
    password_salt: str      # Addition to UserResponseModel
