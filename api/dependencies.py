import motor.motor_tornado
import os

class DBHandlerInitializer:
    def __init__(self, uri):
        print("Connecting to database...")
        self.client = DBHandler.db_handler_client = motor.motor_tornado.MotorClient(uri)
        self.db = DBHandler.db_handler = self.client.get_default_database()
        DBHandler.initialized = True

    def get_db_handler(self):
        return self.db

    def  get_client_handler(self):
        return self.client

class DBHandler:
    db_handler_client = None
    db_handler = None
    initialized = False

    def get_db_handler(self, tries = 0):
        if DBHandler.initialized is True:
            return DBHandler.db_handler
        elif tries < 5:
            print("Handler not initialized. Trying again...")
            initiazer = DBHandlerInitializer(os.environ['MONGODB_URI'])
            return get_db_handler(tries+1)
        else:
            print("Handler not initialized. Number of tries exceeded. Exiting!")
