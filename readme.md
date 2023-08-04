# ASTRA-ALGO-TRADER
Automated Stock Trader Bot and Utility software


## Database interface
- Write the scrip_name in the Backtester function and it will fetch data (you don't know what happens in background)
- It first searches the cache files => database => fetches from broker => puts in db & cache
- Carries on with the task you were performing

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



## Ongoing issues

- Set different strategies for different stocks based on Short-term or long-term
- Identify if the strategy is actually worth live-trading
- 

# Idea

Decision: Basic Logic + Mathematical logic + Risk factor 

Basic Logic: Current > Bought + 5-10rs (count decisions) 
Basic Logic: The market seems to be rising & or already near a peak 

Mathematical Logic: using a algorithm like momentum, ML ==> RSI, ADX, SMA

Risk Factor: market crashing, stop loss helps, number of decisions dodged (buy/sell) 



