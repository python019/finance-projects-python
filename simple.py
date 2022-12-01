import matplotlib.pyplot as plt
import pandas_datareader as web
import datetime as dt

start = dt.datetime(2019,1,1)
end = dt.datetime.now()

data = web.DataReader('TSLA', 'yahoo', start, end)

plt.plot(data['Close'])
plt.show()