import os 
import psycopg2
from .connection import * 
import json 
from sqlalchemy import create_engine



class db_stat:
    def __init__(self) -> None:
        self.successful_executions = 0  # Successful query executed by the db
        self.unsuccessful_connections=0 # unsuccessful connections 
       

# url = postgresql://kirtipurohit:1234@localhost:127.0.0.1/db_name
class Manager:
    def __init__(self) -> None:
        with open('lib/modules/database/db_credentials.json', 'r') as file: 
            file= file.read() 
            credentials= json.loads(file)
        self.db_name= credentials['DATABASE']
        self.username= credentials['USERNAME']
        self.host= credentials['HOST']
        self.password= credentials['PASSWORD']
    def create_db(self): 
        """Creates db
        Args:
            None
        Returns:
            true value if the db is created. 
        """

        url= f'postgresql://{self.username}:{self.password}@localhost:{self.host}/amm'
        conn = psycopg2.connect(url)
        cursor= conn.cursor() 
        conn.autocommit = True
        cursor.execute("SELECT 1 FROM pg_catalog.pg_database WHERE datname='historical_data';")
        database_exists = cursor.fetchone()
        if not database_exists:
            create_db_query = "CREATE DATABASE historical_data;"
            cursor.execute(create_db_query)
        self.db_name= 'historical_data'
        cursor.close()
        conn.close()
    def add_ohlc_data(self, scrip_name): 
        """ to add historical data based on scripname
        Args:
            scrip name(stock name)
        Returns:
            None 
        """
        if not self.db_name: 
            self.create_db() 
        self.create_ohlc_table(scrip_name)
    
    def dump_data(self, scrip_name=None, historical_data=None): 
        """create ohlc table 
        Args:
            scrip name(stock name)
        Returns:
            None 
        """
        self.create_db() 
        if scrip_name:
            breakpoint()
            engine = create_engine(f'postgresql+psycopg2://{self.username}:{self.password}@localhost:{self.host}/{self.db_name}')
            historical_data.to_sql(scrip_name.lower(), engine, if_exists='replace', index=False, method='multi', chunksize=1000)
         
    def add_new_order(self, new_order):
        pass 
    def add_new_position(self, new_position):
        pass 
    def close_position(self, closed_position): 
        pass 

