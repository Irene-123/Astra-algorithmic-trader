from lib.modules.broker.manager import Manager
scrip_names=['TITAN', 'HDFCBANK']
timeframes=[('2023-01-31 09:15:00', '2023-02-15 09:20:00')]
broker = Manager(scrip_names)
# broker.fetch_candles_per_minute() #TODO: convert to thread
broker.fetch_new_candle(timeframes=timeframes)