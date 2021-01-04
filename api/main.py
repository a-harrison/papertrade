from fastapi import FastAPI
from .routers import users
from .db import UserLogic
from .dependencies import DBHandlerInitializer, DBHandler
import os

app = FastAPI()

pymongo_client = None
db = None
user_logic = None

async def get_db_handler():
    return await DBHandler.get_db_handler()

@app.on_event("startup")
def startup_event():
    ## TODO: Validate that all required environment variables are defined.
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


app.include_router(users.router)
