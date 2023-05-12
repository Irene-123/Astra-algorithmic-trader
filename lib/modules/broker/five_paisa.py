from datetime import datetime
import json
import os
from typing import List

import pandas as pd
import requests
import threading

from py5paisa import FivePaisaClient

from .template import Broker
from lib.modules.exceptions.broker_exceptions import *
from utils.logger import get_logger
import settings


class FivePaisa(Broker):
    """FivePaisa broker instance. Contains functions to interact with FivePaisa API. 
    """
    def __init__(self) -> None:
        super().__init__()
        self.broker_name = "FivePaisa"
        self.logger = get_logger(logger_name=self.broker_name)
        self.fetch_scrip_master()
        self.login()
        self.live_feed_thread = None
        self.live_feed_scrips = []
    
    def login(self):
        """Creates a session with the broker (5Paisa) using two factor authentication

        Returns:
            FivePaisaClient: Client object of the broker
        """
        try:
            with open(settings.BROKER_CREDENTIALS_FILE, 'r') as file:
                self.broker_credentials = json.load(file)['FivePaisa']
        except FileNotFoundError:
            raise CredentialsNotFoundException
        except IndexError:
            raise CredentialsNotFoundException
        
        two_factor_creds={
            "APP_NAME": self.broker_credentials['APP_NAME'],
            "APP_SOURCE": self.broker_credentials['APP_SOURCE'],
            "USER_ID": self.broker_credentials['USER_ID'],
            "PASSWORD": self.broker_credentials['APP_PASSWORD'],
            "USER_KEY": self.broker_credentials['USER_KEY'],
            "ENCRYPTION_KEY": self.broker_credentials['ENCRYPTION_KEY']
        }

        self.client = FivePaisaClient(
            email = self.broker_credentials['EMAIL'], 
            passwd = self.broker_credentials['WEB_PASSWORD'], 
            dob = self.broker_credentials['DOB'],
            cred = two_factor_creds)
        
        self.client.login()
        self.check_connection()
        self.logger.info("Connected with Five Paisa")
        return self.client

    def check_connection(self):
        """Checks if broker connection is live or not

        Raises:
            FailedLoginException: Login not successful

        Returns:
            bool: True for live connection
        """
        if self.client.client_code in ["", "INVALID CODE"]:
            raise FailedLoginException
        return True

    def fetch_scrip_master(self):
        """Fetches scrip master table data.
        """
        file_path = settings.SCRIP_MASTER_FILE
        if os.path.exists(file_path):
            m_dt = datetime.fromtimestamp(os.path.getmtime(settings.SCRIP_MASTER_FILE))
            m_dt = m_dt.date()  # Extracting date
            
        if not os.path.exists(file_path) or m_dt != datetime.now().date():  # If file not exists or file was not modified today
            url = "https://images.5paisa.com/website/scripmaster-csv-format.csv"
            res = requests.get(url, allow_redirects=True)
            self.logger.info("Downloading Scrip master file")
            file = open(settings.SCRIP_MASTER_FILE, 'wb')
            file.write(res.content)
            file.close()
        
        file = open(settings.SCRIP_MASTER_FILE, 'r')
        self.instruments = pd.read_csv(file).astype(str)
        file.close()
        self.logger.info('Srcip master file loaded')

    def convert_value(self, from_type:str, to_type:str, value:str) -> str:
        """Convert value by matching it from the scrip master table

        Args:
            from_type (str): type of parameter to convert from
            to_type (str): type of parameter to convert to
            value (str): value of the parameter

        Raises:
            InvalidPropertyTypeException: Property does not exists in the scrip master table
            PropertyValueNotFoundException: Property value does not exists in the scrip master table

        Returns:
            str: converted value of the parameter
        """
        types = ["Exch", "ExchType", "Scripcode", "Name", "Series", "Expiry", "CpType", "StrikeRate", "WireCat", 
                 "ISIN", "FullName", "LotSize", "AllowedToTrade", "QtyLimit", "Multiplier", "Underlyer", "Root" ,"TickSize", "CO BO Allowed"]

        if from_type not in types or to_type not in types:
            raise InvalidPropertyTypeException
        
        try:
            return str(self.instruments[self.instruments[from_type] == str(value)][to_type].iloc[0])
        except IndexError:
            raise PropertyValueNotFoundException
    
    def place_order(self, order_type, scrip_name, price, quantity, is_intraday):
        """Places order with the broker

        Args:
            order_type (str): BUY or SELL
            scrip_code (int): Unique scrip code of the stock
            price (float): Trading price, 0 for market order
            quantity (int): Quantity to trade
            is_intraday (bool): True for intraday order

        Returns:
            status (bool): order successfully placed or not
            order_id (int): unique order id, -1 for failure 
        """
        scrip_code = self.convert_value(from_type="Name", to_type="Scripcode", value=scrip_name)
        response = self.client.place_order(
            OrderType = 'B' if order_type == "BUY" else "S",
            Qty = int(quantity),
            Exchange = self.convert_value(from_type="Scripcode", to_type="Exch", value=scrip_code),
            ExchangeType = self.convert_value(from_type="Scripcode", to_type="ExchType", value=scrip_code),
            Price = None if float(price) == 0 else float(price),
            ScripCode = int(scrip_code),
            IsIntraday = bool(is_intraday)
        )
        #TODO Check for success status
        if response['RMSResponseCode'] < 0:
            return False, response['Message']
        return True, response['BrokerOrderID']

    def fetch_historical_data(self, scrip_name:str, time_interval:str, from_dt:str, to_dt:str) -> pd.DataFrame:
        """Fetches historical data for the provided scrip

        Args:
            scrip_name (str): Name of the scrip
            time_interval (str): 1m, 5m, 10m, 15m, 30m, 60m, 1d
            from_dt (str): Starting date of the data (YYYY-MM-DD)
            to_dt (str): Ending date of the data (YYYY-MM-DD)

        Returns:
            pd.DataFrame: Dataframe consisting ohlcv data
        """
        scrip_code = self.convert_value(from_type="Name", to_type="Scripcode", value=scrip_name)
        historical_data = self.client.historical_data(
            Exch = self.convert_value(from_type="Scripcode", to_type="Exch", value=scrip_code),
            ExchangeSegment = self.convert_value(from_type="Scripcode", to_type="ExchType", value=scrip_code),
            ScripCode = int(scrip_code),
            time = time_interval,
            From = from_dt,
            To = to_dt
        )
        return historical_data
            
    def subscribe_scrips(self, scrip_names:list):
        #TODO
        """Subscribes to the given scrips, and starts live streaming

        Args:
            scrip_names (list[str]): List containing scrip names
        """
        def on_message(ws, message):
            print(ws)
            print(message)

        request_list = list()
        for scrip_name in scrip_names:
            scrip_code = self.convert_value(from_type="Name", to_type="Scripcode", value=scrip_name)
            request_list.append({
                "Exch": self.convert_value(from_type="Scripcode", to_type="Exch", value=scrip_code),
                "ExchType": self.convert_value(from_type="Scripcode", to_type="ExchType", value=scrip_code),
                "ScripCode": scrip_code
            })
            print(request_list)

        req_data = self.client.Request_Feed('mf','s',request_list)  # MarketFeedV3, Subscribe
        self.client.connect(req_data)
        self.live_feed_thread = threading.Thread(target=self.client.receive_data, args=(on_message,))
        self.live_feed_thread.start()


