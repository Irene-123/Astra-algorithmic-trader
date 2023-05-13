from sqlalchemy import create_engine
import pandas as pd

import settings
from .connection import *


class db_stat:
    def __init__(self) -> None:
        self.successful_executions = 0      # Successful query executed by the db
        self.unsuccessful_connections = 0   # unsuccessful connections 
       

class Manager:
    def __init__(self) -> None:
        self.setup_db()

    def setup_db(self): 
        """Creates historical and user databases
        
        Returns:
            bool: True for successful creation 
        """
        conn = connect_db(DEFAULT_DB)
        cursor = conn.cursor() 

        try:
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname='{settings.HISTORICAL_DB}';")
            database_exists = cursor.fetchone()
            if not database_exists:
                create_db_query = f"CREATE DATABASE {settings.HISTORICAL_DB};"
                cursor.execute(create_db_query)
            
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname='{settings.USER_DB}';")
            database_exists = cursor.fetchone()
            if not database_exists:
                create_db_query = f"CREATE DATABASE {settings.USER_DB};"
                cursor.execute(create_db_query)
        except Exception as e:
            raise QueryFailedException(e)

        cursor.close()
        conn.close()

    def add_historical_data(self, scrip_name:str, candle_data:pd.DataFrame): 
        """Add or update historical data

        Args:
            scrip name (str): Unique scrip name
            candle_data (pd.DataFrame): Candle data to add or update
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

