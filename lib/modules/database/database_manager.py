import os 
import psycopg2
from .connection import connect_db 

class db_stat:
    def __init__(self) -> None:
        self.successful_executions = 0  # Successful query executed by the db
        self.unsuccessful_connections=0 # unsuccessful connections 
       

# url = postgresql://kirtipurohit:1234@localhost:127.0.0.1/db_name
class Manager:
    def __init__(self) -> None:
        pass
    def connect(self, connection_url):
        self.cursor= connect_db(connection_url)
    def execute_query(self, query):
        self.cursor.execute(query) 

# Run as import database.database_manager obj= Manager() obj.connect(postgresql://kirtipurohit:1234@localhost:127.0.0.1/db_name)