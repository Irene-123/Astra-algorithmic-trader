# from lib.modules.broker.manager import Manager
# scrip_names=['SUNPHARMA']
# timeframes=[('2023-01-15 09:20:00', '2023-06-14 03:00:00')]
# broker = Manager(scrip_names)
# # # broker.fetch_candles_per_minute() #TODO: convert to thread
# broker.fetch_new_candle(timeframes=timeframes)


from multiprocessing import Queue
from lib.backtesting.results import *
from lib.backtesting.backtester import Backtester
from lib.backtesting.results import *


backtester= Backtester()
backtester.run_backtest(["SUNPHARMA"])
generate_plot_adx_rsi("SUNPHARMA")