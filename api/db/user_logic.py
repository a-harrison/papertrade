from ..dependencies import DBHandler
from fastapi import Depends
from pydantic import BaseModel
from datetime import datetime
from ..models import UserException
from base64 import b64encode
from os import urandom
import hashlib


## Class to contain all the logic for querying the database
## and retrieving user information.
class UserLogic:
    def __init__(self):
        self.db = DBHandler.get_db_handler(self)

    async def get_user_by_id(self, user_id: str):
        user = await self.db.users.find_one({ "_id" : user_id })
        return user

    async def get_user_by_username(self, username: str):
        user = await self.db.users.find_one({ "username" : username })
        return user

    async def get_user_by_email(self, email: str):
        user = await self.db.users.find_one({ "email" : email })
        return user

    # ObjectId values are monotonically increasing
    # So we'll manually generate a random string just in case we eventually want
    # to shard.
    async def generate_new_id(self):
        ## Manually generate new _id string value
        _id = b64encode(urandom(16)).decode('utf-8')

        # The impossible case that we randomly generate a value
        # that already exists.
        if await UserLogic.get_user_by_id(self, _id) is not None:
            return await UserLogic.generate_new_id(self)
        else:
            return _id

    ## Create user based on given user object.
    ## The important part here is how we're going to securely handle the
    ## salting and hashing of the password.
    ##
    ## We should get a client_hash when creating the user. We need to salt and
    ## re-hash that again.
    async def create_user(self, user):
        _id = await UserLogic.generate_new_id(self)
        username = user.username.lower()        ## Usernames are case insensitive
        email = user.email.lower()              ## lowercase email address
        # We go through password hashing first before checking if user exists
        salt = urandom(48)
        hashed_password = hashlib.pbkdf2_hmac(
            'sha256',                           ## Hash name
            user.client_hash.encode('utf-8'),    ## Password
            salt,                               ## Salt
            100000                              ## Repetition is important
        )

        if await UserLogic.get_user_by_username(self, username) is not None:
            raise UserException("A user with this username already exists.")

        elif await UserLogic.get_user_by_email(self, email) is not None:
            raise UserException("A user with this email address already exists.")

        else:
            ## Create user
            user_result = await self.db.users.insert_one({
                "_id" : _id,
                "username" : username,
                "email" : user.email,
                "hashed_password" : hashed_password,
                "salt" : salt,
                "enabled" : True,
                "creation_date" : datetime.utcnow()
            })
            return user_result.inserted_id

    async def delete_user_by_id(self, user_id: str):
        result = await self.db.users.delete_one({ "_id" : user_id })
        if result.deleted_count == 0:
            raise UserException("User not found.")
        else:
            return 1
