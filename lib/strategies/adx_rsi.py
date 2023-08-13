import pandas as pd
from datetime import datetime, timedelta
import time

from multiprocessing import Queue
from lib.strategies.template import Strategy, TradeCall

def get_adx(high, low, close, lookback):
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    
    tr1 = pd.DataFrame(high - low)
    tr2 = pd.DataFrame(abs(high - close.shift(1)))
    tr3 = pd.DataFrame(abs(low - close.shift(1)))
    frames = [tr1, tr2, tr3]
    tr = pd.concat(frames, axis = 1, join = 'inner').max(axis = 1)
    atr = tr.rolling(lookback).mean()
    
    plus_di = 100 * (plus_dm.ewm(alpha = 1/lookback).mean() / atr)
    minus_di = abs(100 * (minus_dm.ewm(alpha = 1/lookback).mean() / atr))
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    adx = ((dx.shift(1) * (lookback - 1)) + dx) / lookback
    adx_smooth = adx.ewm(alpha = 1/lookback).mean()
    return plus_di, minus_di, adx_smooth



# RSI CALCULATION

def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    for item in ret.items():
        if item[1] < 0:
            up.append(0)
            down.append(item[1])
        else:
            up.append(item[1])
            down.append(0)
    
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    
    up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
    
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    
    return rsi_df[3:]

    

class ADX_RSI(Strategy):
    def __init__(self, manager_ipc: Queue, time_interval:str="1d") -> None:
        super().__init__(name="adx_rsi", manager_ipc=manager_ipc)
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
        i= self.historical_data[scrip].index[self.historical_data[scrip]['Datetime'] == datetime].tolist()[0]
        data= self.historical_data[scrip]
        data['plus_di'] = pd.DataFrame(get_adx(data['High'], data['Low'], data['Close'], 14)[0]).rename(columns = {0:'plus_di'})
        data['minus_di'] = pd.DataFrame(get_adx(data['High'], data['Low'], data['Close'], 14)[1]).rename(columns = {0:'minus_di'})
        data['adx'] = pd.DataFrame(get_adx(data['High'], data['Low'], data['Close'], 14)[2]).rename(columns = {0:'adx'})
        data = data.dropna()

        data['rsi_14'] = get_rsi(data['Close'], 14)
        data = data.dropna()
        adx = data['adx']
        pdi = data['plus_di']
        ndi = data['minus_di']
        rsi = data['rsi_14'] 
        
        if_sell = adx[i] > 25 and pdi[i] < ndi[i] and rsi[i] < 30
        if_buy= adx[i] < 25 and pdi[i] > ndi[i] and rsi[i] > 70
        
        if if_sell: 
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
            
        elif if_buy:
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
            # if self.current_call[scrip] == None or self.current_call[scrip] == "BUY":
            #     self.current_call[scrip] = "SELL"
            #     self.current_price[scrip] = None 
            #     # self.manager_ipc.put(TradeCall(scrip=scrip, call="SELL"))
            #     return TradeCall(
            #     call_type = "SELL",
            #     order_type = "LIMIT",
            #     price = self.historical_data[scrip]['Close'].iloc[-1],
            #     stoploss = 1.05 * self.historical_data[scrip]['Close'].iloc[-1],
            #     trailing_stoploss = 0.005 * self.historical_data[scrip]['Close'].iloc[-1]
            # )
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
    