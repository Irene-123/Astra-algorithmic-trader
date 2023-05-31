from abc import ABC, abstractmethod
import socket
import json
import threading
from multiprocessing import Queue

from utils.logger import get_logger

class TradeCall:
    def __init__(self, call_type:str="NONE", order_type:str="NONE", price:float=0, stoploss:float=0, trailing_stoploss:float=0) -> None:
        self.call_type = call_type
        self.order_type = order_type
        self.price = price
        self.stoploss = stoploss
        self.trailing_stoploss = trailing_stoploss

class Strategy(ABC):
    def __init__(self, name:str, manager_ipc:Queue) -> None:
        self.ticker_port = 12380
        self.ticker_data = {}
        self.name = name
        self.manager_ipc = manager_ipc
        self.logger = get_logger(logger_name = name)

    def start_live_feed(self, scrip_codes:list):
        """Starts live feed from the broker manager

        Args:
            scrip_codes (list): List of scrip codes for live feed
        """
        def live_feed(self):
            while True:
                data = json.loads(self.soc.recv(1024).decode())
                self.ticker_data[data['code']] = data['value']
        
        self.soc = socket.socket()
        self.soc.connect(('127.0.0.1', self.ticker_port))
        codes = json.dumps({"codes": scrip_codes}, indent=4)
        self.soc.send(codes.encode())
        self.live_feed_thread = threading.Thread(target=live_feed, args=())
        self.live_feed_thread.start()

    def send_call(self, call_type:str, call_price:float=None):
        """Send trade call to the strategy manager

        Args:
            call_type (str): BUY or SELL
            call_price (float): Price of trade, None means market order
        """
        call = {
            "strategy": self.name,
            "call_type": call_type,
            "call_price": call_price
        }
        self.manager_ipc.put(call)

    def fetch_candle(self, scrip:str, time_interval:str):
        """Fetches historical data for the given time interval

        Args:
            scrip (str): Unique scrip name
            time_interval (str): 1m, 5m, 60m, 1d
        """
        pass

    def get_historical_data(self, scrip, start_date, end_date, time_interval):
        pass

    @abstractmethod
    def run_strategy(self, scrips:list):
        pass

