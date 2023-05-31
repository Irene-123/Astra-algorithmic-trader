from lib.modules.broker.manager import Manager
scrip_names=['TITAN', 'HDFCBANK']
broker = Manager(scrip_names)
broker.fetch_candles_per_minute()

