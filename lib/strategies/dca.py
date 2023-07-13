"""
Dollar-cost averaging is the practice of systematically investing equal amounts of money 
at regular intervals, regardless of the price of a security.

Strategy for regualar & systematic investment. 
"""
from datetime import datetime, timedelta
import time
import pandas as pd

from multiprocessing import Queue
from lib.strategies.template import Strategy, TradeCall

class DCA(Strategy):
    def __init__(self, manager_ipc: Queue, time_interval:str="1d") -> None:
        super().__init__(name="dca", manager_ipc=manager_ipc)
        self.current_call = {}
        self.current_price = {}
        self.historical_data = {}
        self.is_strategy_initialized = False 
        self.time_interval = time_interval
        self.i = 0
        self.look_back = 30 # days
        self.min_max_threshold = 0.03 # 5%

    def initialize_strategy(self, scrips:list, historical_data:dict=None):
        """Initialize strategy with the starting metadata after which it can work candle by candle

        Args:
            scrips (list): List of scrip names
            historical_data (dict, optional): Historical data to initialize with during backtesting. Defaults to None.
        """
        if self.is_strategy_initialized:    # Initialize strategy only once
            return
        for scrip in scrips:
            if historical_data is None:
                self.historical_data[scrip] = self.get_historical_data(scrip=scrip, start_date=None, end_date=None, time_interval=self.time_interval)
            else:   # backtesting
                self.historical_data[scrip] = historical_data[scrip]
            self.current_call[scrip] = None
        self.is_strategy_initialized = True

    def get_historical_data(self, scrip, start_date, end_date, time_interval):
        pass

    def add_new_candle(self, scrip:str, candle: pd.DataFrame):
        self.historical_data[scrip] = self.historical_data[scrip]._append(candle, ignore_index=True)

    def run_logic(self, scrip:str, datetime= None):
        index= self.historical_data[scrip].index[self.historical_data[scrip]['Datetime'] == datetime].tolist()[0]
        if index < self.look_back:
            return 
        # if self.i % self.look_back==0:
        start_index = index - self.look_back 
        # breakpoint()
        previous_values = self.historical_data[scrip].iloc[start_index:index]['Close']
        close_lb_df = pd.Series(previous_values)
        min_price = close_lb_df.min()
        max_price = close_lb_df.max()
        min_price_threshold = min_price * (1 + self.min_max_threshold)
        max_price_threshold = max_price * (1 - self.min_max_threshold)
        if self.historical_data[scrip]['Close'].iloc[-1] <= min_price_threshold:
            if self.current_call[scrip] == None or self.current_call[scrip] == "SELL":
                self.current_call[scrip] = "BUY"
                self.current_price[scrip] = self.historical_data[scrip]['Close'].iloc[-1]
                # self.manager_ipc.put(TradeCall(scrip=scrip, call="BUY"))
                return TradeCall(
                call_type = "BUY",
                order_type = "LIMIT",
                price = self.historical_data[scrip]['Close'].iloc[-1],
                stoploss = 0.90 * self.historical_data[scrip]['Close'].iloc[-1],
                trailing_stoploss = 0.005 * self.historical_data[scrip]['Close'].iloc[-1]
            )
            
        if self.historical_data[scrip]['Close'].iloc[-1] >= max_price_threshold and self.current_price[scrip] != None \
            and self.historical_data[scrip]['Close'].iloc[-1]*(1.09) < self.current_price[scrip]:
            if self.current_call[scrip] == None or self.current_call[scrip] == "BUY":
                self.current_call[scrip] = "SELL"
                self.current_price[scrip] = None 
                # self.manager_ipc.put(TradeCall(scrip=scrip, call="SELL"))
                return TradeCall(
                call_type = "SELL",
                order_type = "LIMIT",
                price = self.historical_data[scrip]['Close'].iloc[-1],
                stoploss = 1.05 * self.historical_data[scrip]['Close'].iloc[-1],
                trailing_stoploss = 0.005 * self.historical_data[scrip]['Close'].iloc[-1]
            )
        return TradeCall() # No trade call

    def run_strategy(self, scrips: list):
        if self.is_strategy_initialized == False:
            self.initialize_strategy()
        while True:
            for scrip in scrips:
                call, price = self.run_logic(scrip)
                if call != "NONE":
                    self.manager_ipc.put(TradeCall(scrip=scrip, call=call))
            time.sleep(60)

    def send_call(self, call_type: str, call_price: float = None):
        pass 
    