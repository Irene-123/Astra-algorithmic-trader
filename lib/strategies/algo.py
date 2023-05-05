from lib.modules.live_data_fetch.API_client import API
obj = API()
client= obj.client
import time 

def sma_strategy(symbol):
    # Get historical data for the symbol
    historical_data = client.historical_data("NFO", symbol, "1D")
    
    # Calculate the 20-day and 50-day simple moving averages
    historical_data["sma20"] = historical_data["close"].rolling(window=20).mean()
    historical_data["sma50"] = historical_data["close"].rolling(window=50).mean()
    
    # Determine the current position based on the moving average crossover
    current_position = ""
    if historical_data["sma20"].iloc[-1] > historical_data["sma50"].iloc[-1]:
        current_position = "BUY"
    elif historical_data["sma20"].iloc[-1] < historical_data["sma50"].iloc[-1]:
        current_position = "SELL"
    
    return current_position


while True:
    # Check the current position for the symbol
    current_position = sma_strategy("NIFTY 50")
    
    # If the current position is "BUY" and we don't already have a position, place a buy order
    if current_position == "BUY" and client.get_positions()["net_sell_qty"] == 0:
        client.place_order("NFO", "NIFTY 50", "BUY", "LIMIT", quantity=1, price=client.ltp("NFO", "NIFTY 50") - 50)
        print("Placed a buy order for NIFTY 50")
    
    # If the current position is "SELL" and we already have a long position, place a sell orderg
    elif current_position == "SELL" and client.get_positions()["net_buy_qty"] > 0:
        client.place_order("NFO", "NIFTY 50", "SELL", "LIMIT", quantity=1, price=client.ltp("NFO", "NIFTY 50") + 50)
        print("Placed a sell order for NIFTY 50")
    
    # Wait for 10 seconds before checking the position again
    time.sleep(10)
