import os
import time
import pandas_datareader as pdr
from winotify import Notification, audio

tickers = ["AAPL", "FB", "NVDA", "GS", "WFC"]


upper_limits = [200, 220, 240, 400, 70]
lower_limits = [100, 130, 140, 280, 30]

while True:
    last_prices = [pdr.DataReader(ticker, "yahoo")["Adj Close"][-1] for ticker in tickers]
    time.sleep (1)
    for i in range(len(tickers)):
        if last_prices[i] > upper_limits[i]: 
            toast = Notification(app_id="SUBUX Stock Alarm Bot",
                                title=" Price Alert For " + tickers[i],
                                msg=f"{tickers[i]} has reached a price of {last_prices[i]}. You might want to sell.", 
                                icon=os.path.join(os.getewd(), "src/s.png"), 
                                duration="long")
            toast.add_actions(label="Go to Stockbroker", launch="http://subux.uz/")
            toast.set_audio(audio.LoopingAlarm6, loop=True)
            toast.show()    
        elif last_prices[i] < lower_limits[i]:
            toast = Notification(app_id="SUBUX Stock Alarm Bot",
                                title=" Price Alert For " + tickers[i],
                                msg=f"{tickers[i]} has reached a price of {last_prices[i]}. You might want to buy.", 
                                icon=os.path.join(os.getewd(), "src/cash.png"), 
                                duration="long")
            toast.add_actions(label="Go to Stockbroker", launch="http://subux.uz/")
            toast.set_audio(audio.LoopingAlarm8, loop=True)
            toast.show() 
        time.sleep(1)