import pandas as pd
import matplotlib.pyplot as plt

def generate_plot():
    dataset = pd.read_csv("SBIN-backtest.csv", index_col=0)

    trades = dataset[["Action", "Price"]]
    trades = trades[trades["Action"] != "NONE"]
    buy_trades_x, buy_trades_y = list(), list()
    sell_trades_x, sell_trades_y = list(), list()
    for ind, row in trades.iterrows():
        if row["Action"] == "BUY":
            buy_trades_x.append(ind)
            buy_trades_y.append(float(row["Price"]))
        else:
            sell_trades_x.append(ind)
            sell_trades_y.append(float(row['Price']))


    plt.plot(dataset['Close'], label="Close price")
    plt.plot(dataset['Sma20'], label="sma-20")
    plt.plot(dataset['Sma50'], label="sma-50")
    plt.scatter(buy_trades_x, buy_trades_y, marker='o', color='green')
    plt.scatter(sell_trades_x, sell_trades_y, marker='o', color='red')
    plt.legend(loc=0)
    plt.show()