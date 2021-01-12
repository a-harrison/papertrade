from fastapi.security import OAuth2PasswordBearer
import motor.motor_tornado
import os

class DBHandler:
    db_handler_client = None
    db_handler = None
    initialized = False

    uri = os.environ['MONGODB_URI']
    db_handler_client2 = motor.motor_tornado.MotorClient(uri)
    db_handler2 = db_handler_client2.get_default_database()

    # def get_db_handler(self, tries = 0):
    #     if DBHandler.initialized is True:
    #         return DBHandler.db_handler
    #     elif tries < 5:
    #         print("Handler not initialized. Trying again...")
    #         initiazer = DBHandlerInitializer(os.environ['MONGODB_URI'])
    #         return get_db_handler(tries+1)
    #     else:
    #         print("Handler not initialized. Number of tries exceeded. Exiting!")

    def get_db_handler(self, tries = 0):
        return DBHandler.db_handler2

class AuthScheme:
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
