from py5paisa import FivePaisaClient
import requests
from datetime import datetime
import json
import os
import pandas as pd
import settings


class API:
    """Object for fivePaisa broker. Acts as a helper utility for interacting with fivePaisa.
    """
    def __init__(self) -> None:
        try:
            with open(settings.BROKER_CREDENTIALS_FILE, 'r') as file:
                self.broker_credentials = json.load(file)
        except FileNotFoundError as e:
            raise Exception("Broker credentials could not be found, process quitting ...")
    
        self.broker_name = self.broker_credentials['BROKER_NAME']
        self.fetch_scrip_master()
        self.client = self.login()
        self.socket_data= pd.DataFrame() 
        self.subscribe_scrips(['SBIN', 'TITAN', 'FOSECOIND', 'HDFCBANK', 'MRF', 'AMBUJACEM', 'TATAMOTORS'])

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
        print("Logged in!")
        client.login()
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
            print("Updating scrip Master")
            file = open(settings.SCRIP_MASTER_FILE, 'wb')
            file.write(res.content)
            file.close()
        print('Srcip master file downloaded')
        file = open(settings.SCRIP_MASTER_FILE, 'r')
        self.instruments = pd.read_csv(file)
        file.close()

    def full_market_snapshot(self): 
        a=[{"Exchange":"N","ExchangeType":"C","Symbol":"RELIANCE"},
                {"Exchange":"N","ExchangeType":"D","Symbol":"BANKNIFTY 31 Mar 2022 CE 35600.00"},
                ]
        df= self.client.fetch_market_depth_by_symbol(a)
        print(df) 
        df.to_csv('marketSnapshot.csv')
            
    def get_scrip_code_from_symbol(self, symbol):
        """Matches symbol in scrip master file to get the scrip code

        Args:
            symbol (str): Symbol for stock/option/derivative

        Returns:
            int: scrip code, -1 in case not found
        """
        try:
            return str(self.instruments[self.instruments['Name'] == symbol]['Scripcode'].iloc[0])
        except IndexError as e:
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
        except IndexError as e:
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
        except IndexError as e:
            return "N"
    #TODO
    def subscribe_scrips(self, symbol_lists):
        """Subsribes to the symbols, and starts there live streaming

        Args:
            symbol_lists (list<str>): List containing symbols for stock/option/derivative
        """
        def on_message(ws, message):
            print(ws)
            print(message[1:-1]) 
            # breakpoint()
            values= json.loads(message[1:-1]) 
            d = pd.DataFrame([values])
            self.socket_data= pd.concat([self.socket_data, d]) 
            self.socket_data.to_csv(r'socket_data.csv')

        request_list = list()
        for symbol in symbol_lists:
            request_list.append({
                "Exch": self.get_exchange_from_symbol(symbol),
                "ExchType": self.get_exchange_type_from_symbol(symbol),
                "ScripCode": self.get_scrip_code_from_symbol(symbol)
            })
        req_data = self.client.Request_Feed('mf','s',request_list)  # MarketFeedV3, Subscribe
        self.client.connect(req_data)
        self.client.receive_data(on_message)
