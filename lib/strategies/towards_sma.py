from datetime import datetime, timedelta
import time

from multiprocessing import Queue
from lib.strategies.template import Strategy


class TowardsSMA(Strategy):
    def __init__(self, manager_ipc: Queue) -> None:
        super().__init__(manager_ipc)
        self.current_call = {}
        self.historical_data = {}

    def run_strategy(self, scrips:list):
        for scrip in scrips:
            self.historical_data[scrip] = self.get_historical_data(scrip=scrip, start_date=None, end_date=None, time_interval="1m")
            self.historical_data[scrip]["sma20"] = self.historical_data[scrip]["close"].rolling(window=20).mean()
            self.historical_data[scrip]["sma50"] = self.historical_data[scrip]["close"].rolling(window=50).mean()
            self.current_call[scrip] = None

        while True:
            for scrip in scrips:
                if self.historical_data[scrip]["sma20"].iloc[-1] > self.historical_data[scrip]["sma50"].iloc[-1]:
                    if self.current_call[scrip] == None or self.current_call[scrip] == "SELL":
                        self.send_call(call_type="BUY", call_price=self.historical_data[scrip]["close"].iloc[-1] - 50)
                        self.current_call[scrip] = "BUY"

                elif self.historical_data[scrip]["sma20"].iloc[-1] < self.historical_data[scrip]["sma50"].iloc[-1]:
                    if self.current_call[scrip] == None or self.current_call[scrip] == "BUY":
                        self.send_call(call_type="SELL", call_price=self.historical_data[scrip]["close"].iloc[-1] + 50)
                        self.current_call[scrip] = "SELL"
            
            last_candle = datetime.strptime(self.historical_data[scrips[0]].iloc[-1]['timestamp'], "%Y%m%d %H:%M:S")
            while datetime.now() < last_candle + timedelta(minutes=1):
                time.sleep(1)