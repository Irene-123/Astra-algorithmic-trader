from sqlalchemy import create_engine
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import settings
from .connection import *


class db_stat:
    def __init__(self) -> None:
        self.successful_executions = 0      # Successful query executed by the db
        self.unsuccessful_connections = 0   # unsuccessful connections 
       

class Manager:
    def __init__(self) -> None:
        try:
            with open(settings.DB_CREDENTIALS_FILE, 'r') as file: 
                self.credentials = json.load(file)
        except FileNotFoundError:
            raise CredentialsNotFoundException
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
            historical_db= self.credentials["ASTRA_HISTORICAL_DATA"]["DATABASE"]
            cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{historical_db}'")
            exists = cursor.fetchone()
            if not exists: 
                create_db_query = f"CREATE DATABASE {historical_db};"
                cursor.execute(create_db_query)
            
            # user_db= credentials["ASTRA_USER_DB"]["DATABASE"]
            # cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{user_db}'")
            # exists = cursor.fetchone()
            # if not exists: 
            #     create_db_query = f"CREATE DATABASE {user_db};"
            #     cursor.execute(create_db_query)
        except Exception as e:
            raise QueryFailedException(e)
        cursor.close() 
        conn.close() 
    
    def dump_historical_data(self, scrip_name=None, historical_data=None): 
        """create ohlc table 
        Args:
            scrip name(stock name)
        Returns:
            None 
        """
        scrip_name= scrip_name.lower() 
        conn= connect_db('ASTRA_HISTORICAL_DATA')
        cursor= conn.cursor() 
        conn.autocommit=True 
        table_name= scrip_name
        create_table_sql = f'CREATE TABLE IF NOT EXISTS {table_name} (datetime TIMESTAMP PRIMARY KEY, open FLOAT, high FLOAT, \
        low FLOAT, close FLOAT, volume INTEGER);'
        cursor.execute(create_table_sql)
        column_names = list(historical_data.columns)
        # Define the SQL statement for the INSERT query
        insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES %s"
        # data = [tuple(row) for row in historical_data.itertuples(index=False)]
        data= self.dump_candles_helper(cursor=cursor, table_name=table_name, historical_data=historical_data)
        execute_values(cursor, insert_query, data)
        cursor.close() 
        conn.close() 


    def dump_candles_helper(self, cursor, table_name, historical_data): 
        query = f"SELECT EXISTS(SELECT 1 FROM {table_name})"
        cursor.execute(query)
        has_rows = cursor.fetchone()[0]
        if len(historical_data)==1 or (not has_rows): 
            data = [tuple(row) for row in historical_data.itertuples(index=False)]

        else: #table is not empty 
            order_column = 'datetime'  # Replace with the appropriate column name
            query = f"SELECT * FROM {table_name} ORDER BY {order_column} DESC LIMIT 1"

            cursor.execute(query)
            last_row = cursor.fetchone()
            try: 
                if last_row:
                    fetched_datetime = last_row[0]
            except QueryFailedException as e: 
                raise e + "Could not fetch last column datetime"
            curr_datetime= datetime.strptime(historical_data.at[1, "Datetime"], '%Y-%m-%d Y%H:%M:%S')
            if curr_datetime < fetched_datetime: # select rows after the 
                historical_data['Datetime'] = pd.to_datetime(historical_data['Datetime'])
                rows = historical_data[historical_data['Datetime'] > fetched_datetime]
                data = [tuple(row) for row in rows.itertuples(index=False)]
            data['datetime'] = pd.to_datetime(data['datetime'])
            data['datetime'] = data['datetime'].dt.strftime('%Y-%m-%d %H:%M:%S')
        return data 
    
    def fetch_latest_candle_from_db(self, scrip_name): 
        order_column = 'datetime'
        try:
            conn= connect_db("ASTRA_HISTORICAL_DATA")  
        except ConnectionError as e:
            raise e + f"while fetching the latest candle from {scrip_name}"
        cursor= conn.cursor() 
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_table WHERE tablename = '{scrip_name.lower()}'")
        exists = cursor.fetchone()
        if not exists: 
            return False 
        query = f"SELECT * FROM {scrip_name.lower()} ORDER BY {order_column} DESC LIMIT 1"
        cursor.execute(query)
        last_row = cursor.fetchone()
        return last_row
    
    def fetch_candles_from_db(self, scrip_name, start_datetime, end_datetime): 
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
        if end_datetime < start_datetime: 
            raise RuntimeError("End datetime should be greater than the start time")
        try:
            conn= connect_db("ASTRA_HISTORICAL_DATA")  
        except ConnectionError as e:
            raise e + f"while fetching candles from {scrip_name}"
        cursor= conn.cursor() 
        cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{scrip_name.lower()}' );")
        exists = cursor.fetchone()
        if exists[0] is False: 
            return [] 
        query = f"SELECT * FROM {scrip_name} WHERE datetime >= '{start_datetime}' AND datetime <= '{end_datetime}';"
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows 
    
    def add_new_order(self, new_order):
        pass 

    def add_new_position(self, new_position):
        pass

    def close_position(self, closed_position): 
        pass 

