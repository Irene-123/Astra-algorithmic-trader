
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import requests
from math import floor
from termcolor import colored as cl

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20,10)

# EXTRACTING STOCK DATA

# def get_historical_data(symbol, start_date):
#     api_key = 'YOUR API KEY'
#     api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
#     raw_df = requests.get(api_url).json()
#     df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
#     df = df[df.index >= start_date]
#     df.index = pd.to_datetime(df.index)
#     return df

# aapl = get_historical_data('AAPL', '2010-01-01')
# aapl.tail()

aapl= pd.read_csv("lib/backtesting/data/SUNPHARMA.csv")
# ADX CALCULATION

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

aapl['plus_di'] = pd.DataFrame(get_adx(aapl['High'], aapl['Low'], aapl['Close'], 14)[0]).rename(columns = {0:'plus_di'})
aapl['minus_di'] = pd.DataFrame(get_adx(aapl['High'], aapl['Low'], aapl['Close'], 14)[1]).rename(columns = {0:'minus_di'})
aapl['adx'] = pd.DataFrame(get_adx(aapl['High'], aapl['Low'], aapl['Close'], 14)[2]).rename(columns = {0:'adx'})
aapl = aapl.dropna()
aapl.tail()

# ADX PLOT

# plot_data = aapl[aapl.index >= '2020-01-01']

ax1 = plt.subplot2grid((11,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((11,1), (6,0), rowspan = 5, colspan = 1)
ax1.plot(aapl['Close'], linewidth = 2, color = '#ff9800')
ax1.set_title('AAPL CLOSING PRICE')
ax2.plot(aapl['plus_di'], color = '#26a69a', label = '+ DI 14', linewidth = 3, alpha = 0.3)
ax2.plot(aapl['minus_di'], color = '#f44336', label = '- DI 14', linewidth = 3, alpha = 0.3)
ax2.plot(aapl['adx'], color = '#2196f3', label = 'ADX 14', linewidth = 3)
ax2.axhline(35, color = 'grey', linewidth = 2, linestyle = '--')
ax2.legend()
ax2.set_title('AAPL ADX 14')
plt.show()

# RSI CALCULATION

def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
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

aapl['rsi_14'] = get_rsi(aapl['Close'], 14)
aapl = aapl.dropna()
aapl.tail()

# RSI PLOT

# aapl = aapl[aapl.index >= '2020-01-01']

ax1 = plt.subplot2grid((11,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((11,1), (6,0), rowspan = 5, colspan = 1)
ax1.plot(aapl['Close'], linewidth = 2.5)
ax1.set_title('AAPL STOCK PRICES')
ax2.plot(aapl['rsi_14'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.set_title('AAPL RSI 14')
plt.show()

# RSI ADX PLOT

# plot_data = aapl[aapl.index >= '2020-01-01']

ax1 = plt.subplot2grid((19,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((19,1), (7,0), rowspan = 5, colspan = 1)
ax3 = plt.subplot2grid((19,1), (14,0), rowspan = 5, colspan = 1)

ax1.plot(aapl['Close'], linewidth = 2.5)
ax1.set_title('AAPL STOCK PRICES')

ax2.plot(aapl['rsi_14'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.set_title('AAPL RSI 14')

ax3.plot(aapl['plus_di'], color = '#26a69a', label = '+ DI 14', linewidth = 3, alpha = 0.3)
ax3.plot(aapl['minus_di'], color = '#f44336', label = '- DI 14', linewidth = 3, alpha = 0.3)
ax3.plot(aapl['adx'], color = '#2196f3', label = 'ADX 14', linewidth = 3)
ax3.axhline(35, color = 'grey', linewidth = 2, linestyle = '--')
ax3.legend()
ax3.set_title('AAPL ADX 14')
plt.show()

# TRADING STRATEGY

def adx_rsi_strategy(prices, adx, pdi, ndi, rsi):
    buy_price = []
    sell_price = []
    adx_rsi_signal = []
    signal = 0
    
    for i in range(len(prices)):
        if adx[i] > 35 and pdi[i] < ndi[i] and rsi[i] < 50:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)
                
        elif adx[i] > 35 and pdi[i] > ndi[i] and rsi[i] > 50:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                adx_rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                adx_rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            adx_rsi_signal.append(0)
                        
    return buy_price, sell_price, adx_rsi_signal

buy_price, sell_price, adx_rsi_signal = adx_rsi_strategy(aapl['Close'], aapl['adx'], aapl['plus_di'], aapl['minus_di'], aapl['rsi_14'])

# POSITION

position = []
for i in range(len(adx_rsi_signal)):
    if adx_rsi_signal[i] > 1:
        position.append(1)
    else:
        position.append(0)
        
for i in range(len(aapl['Close'])):
    if adx_rsi_signal[i] == 1:
        position[i] = 1
    elif adx_rsi_signal[i] == -1:
        position[i] = 0
    else:
        position[i] = position[i-1]
        

adx = aapl['adx']
pdi = aapl['plus_di']
ndi = aapl['minus_di']
rsi = aapl['rsi_14'] 
close_price = aapl['Close']
adx_rsi_signal = pd.DataFrame(adx_rsi_signal).rename(columns = {0:'adx_rsi_signal'}).set_index(aapl.index)
position = pd.DataFrame(position).rename(columns = {0:'adx_rsi_position'}).set_index(aapl.index)

frames = [close_price, adx, pdi, ndi, rsi, adx_rsi_signal, position]
strategy = pd.concat(frames, join = 'inner', axis = 1)

strategy

rets = aapl.close.pct_change().dropna()
strat_rets = strategy.adx_rsi_position[1:]*rets

plt.title('Daily Returns')
rets.plot(color = 'blue', alpha = 0.3, linewidth = 7)
strat_rets.plot(color = 'r', linewidth = 1)
plt.show()



from datetime import datetime, timedelta
import time
import pandas as pd

from multiprocessing import Queue
from lib.strategies.template import Strategy, TradeCall

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
    