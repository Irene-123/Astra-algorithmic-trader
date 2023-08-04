import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px 

def generate_plot(scrip):
    dataset = pd.read_csv(f"{scrip}-backtest.csv", index_col=0)

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

def generate_plot_dca(scrip):
    dataset = pd.read_csv(f"lib/backtesting/backtest-data/{scrip}-backtest.csv", index_col=0)
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
    fig = px.line(dataset['Close'])
    fig.add_scatter(x=buy_trades_x, y=buy_trades_y, marker=dict(color="green", size=15), mode="markers", name="Buy")
    fig.add_scatter(x=sell_trades_x, y=sell_trades_y, marker=dict(color="red", size=15), mode="markers", name="Sell")
    fig.show()

def generate_plot_adx_rsi(scrip):
    dataset = pd.read_csv(f"lib/backtesting/backtest-data/{scrip}-backtest.csv", index_col=0)
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
    # breakpoint()
    fig = px.line(dataset['Close'])
    fig.add_scatter(x=buy_trades_x, y=buy_trades_y, marker=dict(color="green", size=15), mode="markers", name="Buy")
    fig.add_scatter(x=sell_trades_x, y=sell_trades_y, marker=dict(color="red", size=15), mode="markers", name="Sell")
    fig.show()