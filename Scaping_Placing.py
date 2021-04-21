#%%
import requests  # for making http requests to binance
import json  # for parsing what binance sends back to us
import pandas as pd  # for storing and manipulating the data we get back
import numpy as np  # numerical python, i usually need this somewhere
import matplotlib.pyplot as plt  # for charts and such
import datetime as dt  # for dealing with times

# Pull data
def get_bars(symbol, interval):
    root_url = 'https://api.binance.com/api/v1/klines'
    url = root_url + '?symbol=' + symbol + '&interval=' + interval
    data = json.loads(requests.get(url).text)
    df = pd.DataFrame(data)
    df.columns = ['open_time',
                  'Open', 'High', 'Low', 'Close', 'Volume',
                  'close_time', 'qav', 'num_trades',
                  'taker_base_vol', 'taker_quote_vol', 'ignore']
    df.index = [dt.datetime.fromtimestamp(x / 1000.0) for x in df.close_time]
    df.drop(['open_time', 'close_time'], axis=1, inplace=True)
    for col in df.columns:
        df[col] = df[col].astype(float)
    return df

def choose_coin(symbol:str, interval:str):
    coins = get_bars(symbol, interval)
    return coins
#sym = 'ETHBUSD' #ethbusd = get_bars(sym, '1d')

#Ploting Data
char = input('Insert Coins securities ticker:')
sym = choose_coin(char, '1d')
#plt.figure(figsize=(8, 5))
#sym['Close'].plot(figsize=(16, 9))
#plt.title(f"Daily Price of {sym}", fontsize=16)
#plt.ylabel("USD", fontsize=12)
#plt.show()

#Reshape Dataframe, choosing only Close price and apply with an indicator
from Indicator import Indicators
myIndicators = Indicators(sym.Close, 12, 26, 9)
# Reshape Dataframe to Stat_frame for back testing (Setting Indicators)
#mydf = myIndicators.genrate_dataframe()
date = sym.index
col = ['Close','short_EMA','long_EMA']
price = sym.Close.values.tolist()
#Indicators
Short_EMA = myIndicators.ema_short()
Long_EMA = myIndicators.ema_long()
macd = myIndicators.MACD_Diver()[0]
signal_line = myIndicators.MACD_Diver()[1]
hist = myIndicators.MACD_Diver()[2]
rsi = myIndicators.RSI(time=14)

data = [price, Short_EMA, Long_EMA]
d= dict(zip(col,data))
mydf = pd.DataFrame(data =d, index= date)
#mydf = pd.concat([mydf, Short_EMA, Long_EMA, macd, signal_line, rsi], axis=1, ignore_index=True)

#Plotting data normally
plt.figure(figsize=(8, 5))
mydf.plot()
plt.title(f"Daily Price of {char} with Indicators", fontsize=16)
plt.ylabel("USD", fontsize=12)
plt.legend()
plt.show()

#Ploting Data with density of EMA
plt.figure(figsize=(8, 5))
ax2 = mydf.Close.plot(label = 'Closed Price')
ax2.fill_between(mydf.index,mydf.short_EMA, mydf.long_EMA ,color = 'k',alpha=0.5)
plt.title(f"Daily Price of {char} with Density", fontsize=16)
plt.ylabel("USD", fontsize=12)
plt.legend()
plt.show()
#%% Place Order, connect to Binance
from binance.client import Client
# Config Keys to connect to binance
api_key = '' #EDIT
api_secret = ''
client = Client(api_key, api_secret)

# ORDER @ MARKET// BUY and SELL
# ORDER @ MARKET// BUY and SELL
def PlaceBUY(amount, symbol):
    candles = client.get_klines(symbol=symbol, interval=Client.KLINE_INTERVAL_1MINUTE, limit=1)
    close = candles[0][4]
    if float(close) * amount < 10:
        return print("NOT ENOUGHT MINIMUM PLACE ORDER")
    client.order_market_buy(
        symbol=symbol,
        quantity=str(amount))
    # > 10USDT
    print("BUY COMPLETE")

def PlaceSELL(symbol):
    n = 3
    trades = client.get_my_trades(symbol=symbol)
    while True:
        try:
            qty = float(trades[0]["qty"]) - float(trades[0]["commission"])
            qty = str(qty)[:n]
            client.order_market_sell(
                symbol=symbol,
                quantity=str(qty))
            # > 10USDT
            print("SELL COMPLETE")
            return
        except:
            n = n - 1
            pass


#%% Line API for Sending a notification
import time
import requests
def Lineconfig(command):
    url = 'https://notify-api.line.me/api/notify'
    token = '7CbTkpjA3BNxQPJF064lVKdrTU2fIwiA63Xv1T9wKwn'  ## EDIT
    header = {'content-type': 'application/x-www-form-urlencoded', 'Authorization': 'Bearer ' + token}
    return requests.post(url, headers=header, data=command)


def sendtext(message):
    # send plain text to line
    command = {'message': message}
    return Lineconfig(command)

def sendimage(url):
	command = {'message':" ",'imageThumbnail':url,'imageFullsize':url}
	return Lineconfig(command)

#sendtext('Testing Very Fundamental on Binance'
        #'-EMA_Cross Strategy & -Density Strategy')
sendimage('https://geeksoncoffee.com/wp-content/uploads/2018/09/Iron-Man-Infinity-Gauntlet-Avengers-4-Fan-Art-2.jpg')
#sendpicfile('https://drive.google.com/file/d/1tAomYLGC_lDVgWEUEXNt9mSvoAR4gUe-/view?usp=sharing')
