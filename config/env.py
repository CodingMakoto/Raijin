import os

import mysql.connector
from dotenv import load_dotenv

class Database:
    """
    Database is made to create a connection with
    the database and return the connection if
    successfull to get the needed user data and
    to close a connection
    """
    def __init__(self):
        self.conn = self.connect()

    def connect(self):
        load_dotenv(dotenv_path="../")
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE"),
            auth_plugin=os.getenv("DB_AUTH_PLUGIN")
        )

    def close(self):
        if self.conn.is_connected():
            self.conn.close()
