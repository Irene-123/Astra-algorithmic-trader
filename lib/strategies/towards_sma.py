from datetime import datetime, timedelta
import time
import pandas as pd

from multiprocessing import Queue
from lib.strategies.template import Strategy, TradeCall


class TowardsSMA(Strategy):
    def __init__(self, manager_ipc: Queue, time_interval:str="1d") -> None:
        super().__init__(name="towards_sma", manager_ipc=manager_ipc)
        self.current_call = {}
        self.historical_data = {}
        self.is_strategy_initialized = False 
        self.time_interval = time_interval

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

            self.historical_data[scrip]["Sma20"] = self.historical_data[scrip]["Close"].rolling(window=20).mean()   # Simple moving average - 20
            self.historical_data[scrip]["Sma50"] = self.historical_data[scrip]["Close"].rolling(window=50).mean()   # Simple moving average - 50
            
            # Setting initial values to the mean of available previous values
            for i in range(min(19, len(self.historical_data[scrip]))):
                self.historical_data[scrip].loc[i, "Sma20"] = self.historical_data[scrip]["Close"][:i+1].mean()
            for i in range(min(49, len(self.historical_data[scrip]))):
                self.historical_data[scrip].loc[i, "Sma50"] = self.historical_data[scrip]["Close"][:i+1].mean()

            self.current_call[scrip] = None
        self.is_strategy_initialized = True

    def add_new_candle(self, scrip:str, candle:pd.DataFrame):
        """Adds new candle to the running dataset

        Args:
            scrip (str): Scrip name for the candle
            candle (pd.DataFrame): Latest candle data
        """
        candle = candle.reset_index()
        candle.loc[0, "Sma20"] = self.historical_data[scrip]["Close"].tail(20).mean()
        candle.loc[0, "Sma50"] = self.historical_data[scrip]["Close"].tail(50).mean()
        self.historical_data[scrip] = pd.concat([self.historical_data[scrip], candle], ignore_index=True)

    def run_logic(self, scrip:str):
        if self.historical_data[scrip]["Sma20"].iloc[-1] > self.historical_data[scrip]["Sma50"].iloc[-1]:
            if self.current_call[scrip] == None or self.current_call[scrip] == "SELL":
                self.current_call[scrip] = "BUY"
                return TradeCall(
                    call_type = "BUY",
                    order_type = "LIMIT",
                    price = 1.005 * self.historical_data[scrip]['Close'].iloc[-1],
                    stoploss = 0.98 * self.historical_data[scrip]['Close'].iloc[-1],
                    trailing_stoploss = 0.005 * self.historical_data[scrip]['Close'].iloc[-1]
                )

        elif self.historical_data[scrip]["Sma20"].iloc[-1] < self.historical_data[scrip]["Sma50"].iloc[-1]:
            if self.current_call[scrip] == None or self.current_call[scrip] == "BUY":
                self.current_call[scrip] = "SELL"
                return TradeCall(
                    call_type = "SELL",
                    order_type = "LIMIT",
                    price = 0.995 * self.historical_data[scrip]['Close'].iloc[-1],
                    stoploss = 1.02 * self.historical_data[scrip]['Close'].iloc[-1],
                    trailing_stoploss = 0.005 * self.historical_data[scrip]['Close'].iloc[-1]
                )
        
        return TradeCall()

    def run_strategy(self, scrips:list):
        if self.is_strategy_initialized == False:
            self.initialize_strategy()
        while True:
            for scrip in scrips:
                call, price = self.run_logic(scrip)
                if call != "NONE":
                    self.send_call(call_type=call, call_price=price)
            
            last_candle = datetime.strptime(self.historical_data[scrips[0]].iloc[-1]['timestamp'], "%Y%m%d %H:%M:S")
            while datetime.now() < last_candle + timedelta(minutes=1):
                time.sleep(1)
            for scrip in scrips:
                self.fetch_candle(scrip, "1d")
                last_candle = datetime.strptime(self.historical_data[scrips[0]].iloc[-1]['timestamp'], "%Y%m%d %H:%M:S")
                #TODO
    
    def run_backtest(self, scrips:list):
        dataset = dict()
        scrips = ["SBIN"]
        dataset = {"SBIN": pd.read_csv("SBIN.csv", index_col=0)}
        
        historical_data = dict()
        for scrip in scrips:
            historical_data[scrip] = dataset[scrip].head(30)
            dataset[scrip] = dataset[scrip].iloc[30:]
        self.initialize_strategy(scrips=scrips, historical_data=historical_data)
        
        for scrip in scrips:
            actions, prices = [], []
            while len(dataset[scrip]) != 0:
                self.add_new_candle(scrip=scrip, candle=dataset[scrip].head(1))
                dataset[scrip] = dataset[scrip].iloc[1:]
                call, price = self.run_logic(scrip)
                actions.append(call)
                prices.append(price)

            trades = pd.DataFrame({"Action": actions, "Price": prices}).reset_index(drop=True)
            self.historical_data[scrip] = self.historical_data[scrip].iloc[30:].reset_index(drop=True)

            self.historical_data[scrip] = pd.concat([self.historical_data[scrip], trades], axis=1)
            self.historical_data[scrip] = self.historical_data[scrip].drop('index', axis=1)
            self.historical_data[scrip].to_csv(f"{scrip}-backtest.csv")


