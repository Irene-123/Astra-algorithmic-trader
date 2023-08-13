import pandas as pd
from lib.strategies.template import TradeCall
from lib.strategies.towards_sma import TowardsSMA
from lib.strategies.dca import DCA
from lib.strategies.adx_rsi import ADX_RSI
from lib.modules.broker.manager import Manager as BrokerManager
from lib.modules.database.database_manager import Manager as DatabaseManager


class Metrics:
    def __init__(self) -> None:
        self.reset()
    
    def add_new_trade(self, value:float):
        if value > 0:
            self.positive_trades += 1
            self.total_profit_from_positive_trades += value
        else:
            self.negative_trades += 1
            self.total_loss_from_negative_trades += value
        
        self.total_trades += 1
        self.total_gains_from_trades += value

    def reset(self):
        self.positive_trades = 0
        self.negative_trades = 0
        self.total_trades = 0
        self.total_profit_from_positive_trades = 0
        self.total_loss_from_negative_trades = 0
        self.total_gains_from_trades = 0

    def __str__(self) -> str:
        return f"""
TRADE METRICS
TOTAL TRADES : {self.total_trades}
POSITIVE TRADES : {self.positive_trades}
NEGATIVE TRADES : {self.negative_trades}
TOTAL PROFIT : {self.total_profit_from_positive_trades}
TOTAL LOSS : {self.total_loss_from_negative_trades}
NET GAIN : {self.total_gains_from_trades}
"""

class Backtester:
    def __init__(self) -> None:
        self.strategy = ADX_RSI(None, "1d")
        self.metrics = Metrics()
        self.reset()

    def reset(self):
        self.is_trade_running = False
        self.last_call = None
        self.metrics.reset()
        self.position = None
        self.trades = {"Datetime":[], "Action":[], "Price": []}

    def generate_trades_csv(self, scrip):
        # breakpoint() 
        trades = pd.DataFrame(self.trades).reset_index(drop=True)
        historical_data = self.strategy.historical_data[scrip].iloc[30:].reset_index(drop=True)
        merged = pd.merge(historical_data, trades, on='Datetime', how='outer')
        # merged = merged.fillna('NA')
        merged.to_csv(f"lib/backtesting/backtest-data/{scrip}-backtest.csv")

    def place_order(self, order_type:str, price:float, timestamp:str):
        self.trades["Datetime"].append(timestamp)
        self.trades["Action"].append(order_type)
        self.trades["Price"].append(price)

        if self.position == None:
            self.position = (order_type, price)
        else:
            if self.position[0] == "BUY":
                self.metrics.add_new_trade(value = price - self.position[1])
            else:
                self.metrics.add_new_trade(value = self.position[1] - price)
            self.position = None

    def check_exit(self, price:float, timestamp:str):
        if self.last_call is not None and self.is_trade_running is True:
            if self.last_call.call_type == "BUY":
                if price <= self.last_call.stoploss:
                    self.place_order(order_type = "SELL", price = price, timestamp = timestamp)
                    self.is_trade_running = False
                    self.last_call = None
                elif price >= self.last_call.stoploss + self.last_call.trailing_stoploss:
                    self.last_call.stoploss += self.last_call.trailing_stoploss
            
            elif self.last_call.call_type == "SELL":
                if price >= self.last_call.stoploss:
                    self.place_order(order_type = "BUY", price = price, timestamp = timestamp)
                    self.is_trade_running = False
                    self.last_call = None
                elif price <= self.last_call.stoploss - self.last_call.trailing_stoploss:
                    self.last_call.stoploss -= self.last_call.trailing_stoploss

    def check_entry(self, price:float, timestamp:str):
        if self.last_call is not None and self.is_trade_running is False:
            if self.last_call.call_type == "BUY":
                if price <= self.last_call.price:
                    self.place_order(order_type = "BUY", price = price, timestamp = timestamp)
                    self.is_trade_running = True
            # elif self.last_call.call_type == "SELL":
            #     if price >= self.last_call.price:
            #         self.place_order(order_type = "SELL", price = price, timestamp = timestamp)
            #         self.is_trade_running = True

    def run_backtest(self, scrips:list):
        dataset = dict()
        for scrip in scrips:
            try:
                dataset[scrip] = pd.read_csv(f"lib/backtesting/data/{scrip}.csv", index_col=0)
            except FileNotFoundError:
                broker= BrokerManager([scrip])
                db_manager= DatabaseManager() 
                broker.fetch_new_candle(timeframes=[('2023-01-15 09:20:00', '2023-06-14 03:00:00')])
                db_manager.save_data_to_csv([scrip])
                dataset[scrip] = pd.read_csv(f"lib/backtesting/data/{scrip}.csv", index_col=0)
               
            dataset[scrip]= dataset[scrip][:2000]
        historical_data = dict()
        # Initialize the strategy with first 30 candles
        for scrip in scrips:
            historical_data[scrip] = dataset[scrip].head(100).reset_index()
            dataset[scrip] = dataset[scrip].iloc[100:].reset_index() 
        
        self.strategy.initialize_strategy(
            scrips = scrips, 
            historical_data = historical_data
        )

        for scrip in scrips:
            while len(dataset[scrip]) != 0:
                candle = dataset[scrip].head(1)
                self.strategy.add_new_candle(scrip=scrip, candle=candle)
                dataset[scrip] = dataset[scrip].iloc[1:]
                self.check_entry(price = float(candle["Close"].iloc[0]), timestamp = candle['Datetime'].iloc[0])
                self.check_exit(price = float(candle["Close"].iloc[0]), timestamp = candle['Datetime'].iloc[0])
                if self.is_trade_running is True:   # only one trade can run at any given time
                    self.strategy.run_logic(scrip, datetime= candle['Datetime'].iloc[0]) # , datetime= candle['Datetime'].iloc[0]
                    continue
                # breakpoint()
                call = self.strategy.run_logic(scrip, datetime= candle['Datetime'].iloc[0])
                # print(call)
                if call!= None and call.call_type != "NONE":    # Trade call received
                    self.last_call = call
            self.generate_trades_csv(scrip)
            print(self.metrics)
            self.reset()