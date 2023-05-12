import os 
import psycopg2
from .connection import * 

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
    def add_ohlc_data(self, excel_file): 
        pass 
    def add_new_order(self, new_order):
        pass 
    def add_new_position(self, new_position):
        pass 
    def close_position(self, closed_position): 
        pass 



# Run as import database.database_manager obj= Manager() obj.connect(postgresql://kirtipurohit:1234@localhost:127.0.0.1/db_name)