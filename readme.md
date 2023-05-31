# ASTRA-ALGO-TRADER
Automated Stock Trader Bot and Utility software


## Database interface

### Fetch candle per minute script. 
- Provide scrip names
  ```
  scrip_names=['TITAN', 'HDFCBANK']
  broker = Manager(scrip_names)
  broker.fetch_candles_per_minute()
  ```
- This will fetch the data from API and dump in database. 

### Fetch candles from database (NO API request) 
 - 2 functions: `fetch_latest_candle()` & `fetch_candles()`
 - They will fetch the data from db, if not present, will fetch from API 
 - and return the `dataframe`


## Components
- Virtual Trading : User simulation with a set of strategies and fixed balance 
- Paper Trading : Strategy execution in virtual environment
- Backtesting : Strategy performance in past data
- Real Trading : Live trading in the market

## API Limits
Trade orders : 200 reqs/minute
Other APIs : 50 reqs/minute


