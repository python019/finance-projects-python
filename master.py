import os
import time
import pandas_datareader as pdr
# from winotify import Notification, audio

tickers = ["AAPL", "FB", "NVDA", "GS", "WFC"]


upper_limits = [200, 220, 240, 400, 70]
lower_limits = [100, 130, 140, 280, 30]

while True:
    last_prices = [pdr.DataReader(ticker, 'yahoo')["Adj Close"][-1] for ticker in tickers]
    print(last_prices)
    time.sleep(1)
    