from datetime import datetime
import json
import os
from typing import List, Dict

import pandas as pd
from py5paisa import FivePaisaClient
import requests
import threading
from lib.modules.exceptions.broker_exceptions import *
from utils.logger import get_logger
import settings


class Broker:
    """FivePaisa broker instance. Contains functions to interact with FivePaisa API. 
    """
    def __init__(self) -> None:
        self.logger = get_logger(logger_name="five_paisa")
        try:
            with open(settings.BROKER_CREDENTIALS_FILE, 'r') as file:
                self.broker_credentials = json.load(file)
        except FileNotFoundError:
            self.logger.critical("Broker credentials file not exists")
            raise BrokerObjectNotCreatedException
    
        self.broker_name = self.broker_credentials['BROKER_NAME']
        self.fetch_scrip_master()
        self.client = self.login()
        self.socket_data = pd.DataFrame()
        self.values=[]
        t = threading.Thread(target=self.subscribe_scrips, args=(['SBIN'],))
        t.start()

    def login(self):
        """Creates a session with the broker (5Paisa) using two factor authentication

        Returns:
            FivePaisaClient: Client object of the broker
        """
        two_factor_creds={
            "APP_NAME": self.broker_credentials['APP_NAME'],
            "APP_SOURCE": self.broker_credentials['APP_SOURCE'],
            "USER_ID": self.broker_credentials['USER_ID'],
            "PASSWORD": self.broker_credentials['APP_PASSWORD'],
            "USER_KEY": self.broker_credentials['USER_KEY'],
            "ENCRYPTION_KEY": self.broker_credentials['ENCRYPTION_KEY']
        }

        client = FivePaisaClient(
            email = self.broker_credentials['EMAIL'], 
            passwd = self.broker_credentials['WEB_PASSWORD'], 
            dob = self.broker_credentials['DOB'],
            cred = two_factor_creds)
        
        client.login()
        if client.client_code in ["", "INVALID CODE"]:
            self.logger.critical("Broker connection cannot be established")
            raise BrokerObjectNotCreatedException
        
        self.logger.info("Connected with FivePaisa")
        return client

    def fetch_scrip_master(self):
        """Fetches scrip master data, which is required for getting scrip codes for every ticker
        """
        file_path = f"{settings.LIVE_DATA_FETCH_DIRECTORY}/scrip_master.csv"
        if os.path.exists(file_path):
            m_dt = datetime.fromtimestamp(os.path.getmtime(f"{settings.LIVE_DATA_FETCH_DIRECTORY}/scrip_master.csv"))
            m_dt = m_dt.date()  # Extracting date
            
        if not os.path.exists(file_path) or m_dt != datetime.now().date():  # If file not exists or file was not modified today
            url = "https://images.5paisa.com/website/scripmaster-csv-format.csv"
            res = requests.get(url, allow_redirects=True)
            self.logger.info("Downloading Scrip master file")
            file = open(settings.SCRIP_MASTER_FILE, 'wb')
            file.write(res.content)
            file.close()
        
        file = open(settings.SCRIP_MASTER_FILE, 'r')
        self.instruments = pd.read_csv(file)
        file.close()
        self.logger.info('Srcip master file loaded')

    def full_market_snapshot(self, scrips:List[Dict]) -> pd.DataFrame:
        """Fetch full market snapshot of the provided scrips

        Args:
            scrips (List[Dict]): List of scrips {Exchange, ExchangeType, Symbol}

        Returns:
            pd.DataFrame: Dataframe of the market snapshot
        """
        scrips_snapshot = self.client.fetch_market_depth_by_symbol(scrips)
        return scrips_snapshot
            
    def get_scrip_code_from_symbol(self, symbol):
        """Matches symbol in scrip master file to get the scrip code

        Args:
            symbol (str): Symbol for stock/option/derivative

        Returns:
            int: scrip code, -1 in case not found
        """
        try:
            return str(self.instruments[self.instruments['Name'] == symbol]['Scripcode'].iloc[0])
        except IndexError:
            return -1
        
    def get_exchange_from_symbol(self, symbol):
        """Matches symbol in scrip master file to get exchange

        Args:
            symbol (str): Symbol for stock/option/derivative

        Returns:
            str: Exchange code, "N" in case not found
        """
        try:
            return self.instruments[self.instruments['Name'] == symbol]['Exch'].iloc[0]
        except IndexError:
            return "N"
    
    def get_exchange_type_from_symbol(self, symbol):
        """Matches symbol in scrip master file to get exchange code

        Args:
            symbol (str): Symbol for stock/option/derivative

        Returns:
            str: Exchange type, "C" in case not found
        """
        try:
            return self.instruments[self.instruments['Name'] == symbol]['ExchType'].iloc[0]
        except IndexError:
            return "N"
    
    def subscribe_scrips(self, symbols:List):
        """Subscribes to the symbols, and starts live streaming

        Args:
            symbol_lists (list[str]): List containing symbols for stock/option/derivative
        """
        def on_message(ws, message):
            print(ws)
            print(message[1:-1]) 
            self.values= json.loads(message[1:-1]) 
            d = pd.DataFrame([self.values])
            self.socket_data = pd.concat([self.socket_data, d]) 
            self.socket_data.to_csv(r'socket_data.csv')

        request_list = list()
        print(symbols)
        for symbol in symbols:
            request_list.append({
                "Exch": self.get_exchange_from_symbol(symbol),
                "ExchType": self.get_exchange_type_from_symbol(symbol),
                "ScripCode": self.get_scrip_code_from_symbol(symbol)
            })
        req_data = self.client.Request_Feed('mf','s',request_list)  # MarketFeedV3, Subscribe
        self.client.connect(req_data)
        self.client.receive_data(on_message)


