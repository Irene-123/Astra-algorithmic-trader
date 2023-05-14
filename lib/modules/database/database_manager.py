from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import settings
from .connection import *
try:
    with open(settings.DB_CREDENTIALS_FILE, 'r') as file: 
        credentials = json.load(file)
except FileNotFoundError:
    raise CredentialsNotFoundException

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
        conn = connect_db('DEFAULT_DB')
        cursor = conn.cursor() 
        conn.autocommit=True
        try:
            historical_db= credentials["ASTRA_HISTORICAL_DATA"]["DATABASE"]
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{historical_db}'")
            exists = cursor.fetchone()
            if not exists: 
                create_db_query = f"CREATE DATABASE {historical_db};"
                cursor.execute(create_db_query)
            
            user_db= credentials["ASTRA_USER_DB"]["DATABASE"]
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{user_db}'")
            exists = cursor.fetchone()
            if not exists: 
                create_db_query = f"CREATE DATABASE {user_db};"
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
        scrip_name= scrip_name.lower() 
        self.setup_db() 
        conn= connect_db('ASTRA_HISTORICAL_DATA')
        cursor= conn.cursor() 
        conn.autocommit=True 
        table_name= credentials['ASTRA_HISTORICAL_DATA']['DATABASE']
        create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} (datetime TIMESTAMP PRIMARY KEY, open FLOAT, high FLOAT, \
        low FLOAT, close FLOAT, volume INTEGER);'
        cursor.execute(create_table_sql)

        column_names = list(historical_data.columns)

        # Define the SQL statement for the INSERT query
        insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES %s"
        data = [tuple(row) for row in historical_data.itertuples(index=False)]
        execute_batch(cursor, insert_query, data)
        cursor.close() 
        conn.close() 

    def add_new_order(self, new_order):
        pass 

    def add_new_position(self, new_position):
        pass

    def close_position(self, closed_position): 
        pass 

