from fastapi import Depends, FastAPI, HTTPException, status
from .routers import me, token, users
from .dependencies import DBHandlerInitializer, DBHandler, AuthScheme
import os

app = FastAPI()

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

app.include_router(me.router)
app.include_router(token.router)
app.include_router(users.router)
