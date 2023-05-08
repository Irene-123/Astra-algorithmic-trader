from abc import ABC, abstractmethod
import socket
import json
import threading
from multiprocessing.connection import PipeConnection


class Strategy(ABC):
    def __init__(self, manager_ipc:PipeConnection) -> None:
        self.ticker_port = 12380
        self.ticker_data = {}
        self.manager_ipc = manager_ipc
        self.run_strategy()

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

    def send_call(self, call_type:str, call_price:float):
        """Send trade call to the strategy manager

        Args:
            call_type (str): BUY or SELL
            call_price (float): Price of trade
        """
        call = {
            "call_type": call_type,
            "call_price": call_price
        }
        self.manager_ipc.send(json.dumps(call))

    def fetch_candle(self, time_interval:str):
        """Fetches historical data for the given time interval

        Args:
            time_interval (str): 1m, 5m, 60m, 1d
        """
        pass

    @abstractmethod
    def run_strategy(self):
        pass

