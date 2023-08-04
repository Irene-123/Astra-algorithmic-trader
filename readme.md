# ASTRA-ALGO-TRADER 🚀

Automated Stock Trader Bot and Utility software 📈💰

## Database Interface 🗄️

- Simply write the `scrip_name` in the Backtester function, and let the magic happen in the background ✨
- The system first checks cache files database and fetches data from the broker if needed then stores in the database and cache
- Continue with your tasks while the data retrieval and storage are taken care of!

### Fetch Candle per Minute Script 🔥

- Provide the `scrip` names, and this script will fetch data from the API and securely dump it into the database 📊

### Fetch Candles from Database (NO API Request)

- Two functions at your service: `fetch_latest_candle()` & `fetch_candles()`
- They efficiently fetch the data from the database, and if not available, gracefully fetch it from the API
- Returns a handy `dataframe` for your analysis and trading strategies

## Components

- **Virtual Trading**: Experience simulation with a set of strategies and a fixed balance. Test the waters before diving into the real market 

- **Paper Trading**: Execute your strategies in a virtual environment with real-world data. Sharpen your skills and refine your approach before trading live.

- **Backtesting**: Test your strategies' performance in the past data. Analyze and optimize your algorithms for better results

- **Real Trading**: Live trading in the actual market. Put your well-tested strategies to the ultimate test and watch your profits grow! 💹💰

## API Limits ⏱️

- Trade orders: 200 reqs/minute
- Other APIs: 50 reqs/minute

## Ongoing Issues 🚧

- Set different strategies for different stocks based on short-term or long-term goals
- Identify if the strategy is actually worth live-trading. Test, analyze, and choose wisely

## Idea 💡

**Decision:** Combine Basic Logic + Mathematical Logic + Risk Factor to craft powerful strategies

- **Basic Logic:** Buy when Current Price > Bought Price + 5-10 Rs (make calculated decisions)
- **Basic Logic:** Identify market trends and predict near peaks
- **Mathematical Logic:** Leverage algorithms like momentum, RSI, ADX, and SMA
- **Risk Factor:** Implement stop-loss mechanisms to mitigate potential market crashes
- **Risk Factor:** Keep track of the number of successful decisions dodged (buy/sell)


---






