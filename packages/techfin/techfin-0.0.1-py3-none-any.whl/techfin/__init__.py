import pandas as pd
pd.set_option('display.float_format', lambda x: '%.5f' % x)
import numpy as np
import yfinance as yf

import matplotlib.pyplot as plt
plt.style.use('seaborn-bright')
plt.rcParams['figure.figsize'] = (15, 8)

'''
==== def plot_Close(data) ==== 

--> data is the entire dataframe having not just Open, Low, High, Close, Volume
--> the function has no return value, it just plots the data

'''
def plot_Close(data):
    data['Close'].plot()
    plt.title('Close Price Graph', fontsize=14)
    plt.xlabel('Year', fontsize=12)
    plt.ylabel('Price', fontsize=12)
    plt.grid()
    plt.show()



'''
# Simple Moving Average 

-- data is the entire dataframe having Open, Low, High, Close, Volume
-- n is the rolling window of SMA
-- the functions return the same datafrane by adding a column SMA corresponding to n
'''
def SMA(data, n):
    for i in n:
        SMA = pd.Series(data['Close'].rolling(window=i).mean(), name = f'SMA_{i}') 
        data = data.join(SMA) 
    
    return data



'''
==== def plot_SMA(data, n) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the SMA values in different columns
--> n is the rolling window of SMA it is "list" data type
--> the function has no return value, it just plots the data

'''
def plot_SMA(data, n):
    plt.title('Simple Moving Average')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.plot(data['Close'],lw=1, label='Close Price')
    for i in n:
        plt.plot(data[f'SMA_{i}'],lw=1, label=f'SMA_{i}')
        
    plt.legend()
    plt.grid()
    plt.show()



'''
==== def EMA(data, n) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> n is the rolling window of EMA it is "list" data type
--> the functions return the same datafrane by adding a columns EMA corresponding to n

'''
def EMA(data, n):
    for i in n:
        EMA = pd.Series(data['Close'].ewm(span=i, min_periods=i).mean(), name = f'EMA_{i}') 
        data = data.join(EMA) 
    
    return data



'''
==== def plot_EMA(data, n) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the EMA values in different columns
--> n is the rolling window of EMA it is "list" data type
--> the function has no return value, it just plots the data

'''
def plot_EMA(data, n):
    plt.title('Exponential Moving Average')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.plot(data['Close'],lw=1, label='Close Price')
    for i in n:
        plt.plot(data[f'EMA_{i}'],lw=1, label=f'EMA_{i}')
        
    plt.legend()
    plt.grid()
    plt.show()



'''
==== def BollingerBands(data, n, factor) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> n is the period for the middle line SMA
--> factor is the multiplier of standard deviation, default=2
--> the functions return the same datafrane by adding columns for each band - upper, lower, middle

'''
def BollingerBands(data, n=20, factor=2):
    SMA = data['Close'].rolling(window=n).mean()
    Std_dev = data['Close'].rolling(window=n).std()
    data['MiddleBand'] = SMA
    data['UpperBand'] = SMA + (factor * Std_dev) 
    data['LowerBand'] = SMA - (factor * Std_dev)
    return data



'''
==== def plot_BollingerBands(data) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the Bollinger values in different columns
--> the function has no return value, it just plots the data

'''
def plot_BollingerBands(data):
    plt.title('Bollinger Bands')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.plot(data['Close'],lw=1, label='Close Price')
    plt.plot(data['UpperBand'],'g',lw=1, label='Upper band')
    plt.plot(data['MiddleBand'],'r',lw=1, label='Middle band')
    plt.plot(data['LowerBand'],'g', lw=1, label='Lower band')
    plt.legend()
    plt.grid()
    plt.show()



'''
==== def Simple_RSI(data, n) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> n is the period for RSI calculation
--> the functions return the same datafrane by adding columns for RSI

'''
def Simple_RSI(data, n):
    data['Close_Diff'] = data['Close'].diff(periods=1)
    data['Upward'] = data['Close_Diff'].clip(lower=0)
    data['Downward'] = data['Close_Diff'].clip(upper=0)
    data['Downward'] = -data['Downward']
    data['Avg_up'] = pd.Series(data['Upward'].rolling(window=n).mean())
    data['Avg_down'] = pd.Series(data['Downward'].rolling(window=n).mean())
    data['RS_Factor'] = data['Avg_up']/data['Avg_down']
    data['S_RSI'] = 100 - 100/(1+data['RS_Factor'])
    data.drop(['Close_Diff', 'Upward', 'Downward', 'Avg_up', 'Avg_down', 'RS_Factor'], axis = 1, inplace=True)
    return data



'''
==== def plot_S_RSI(data, overbought, oversold) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the S_RSI value column
--> the function has no return value, it just plots the data

'''
def plot_S_RSI(data, overbought=85, oversold=25):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    ax1.plot(data['Close'], label='Close')
    ax1.legend()
    ax1.grid()

    ax2.plot(data['S_RSI'], label='Simple RSI', color='teal')
    
    plt.fill_between(data.index, data['S_RSI'], where=(data['S_RSI'] < oversold), alpha=0.25, label='Oversold', color='green')
    plt.fill_between(data.index, data['S_RSI'], where=(data['S_RSI'] > overbought), alpha=0.25, label='Overbought', color='red')
    
    ax2.legend()
    ax2.set_title('Simple RSI Indicator')
    plt.show()



'''
==== def Exponential_RSI(data, n) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> n is the period for RSI calculation
--> the functions return the same datafrane by adding columns for RSI

'''
def Exponential_RSI(data, n):
    data['Close_Diff'] = data['Close'].diff(periods=1)
    data['Upward'] = data['Close_Diff'].clip(lower=0)
    data['Downward'] = data['Close_Diff'].clip(upper=0)
    data['Downward'] = -data['Downward']
    data['Avg_up'] = data['Upward'].ewm(com=n-1, adjust=True, min_periods=n).mean()
    data['Avg_down'] = data['Downward'].ewm(com=n-1, adjust=True, min_periods=n).mean()
    data['RS_Factor'] = data['Avg_up']/data['Avg_down']
    data['E_RSI'] = 100 - 100/(1+data['RS_Factor'])
    data.drop(['Close_Diff', 'Upward', 'Downward', 'Avg_up', 'Avg_down', 'RS_Factor'], axis = 1, inplace=True)
    return data



'''
==== def plot_E_RSI(data, overbought, oversold) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the E_RSI value column
--> the function has no return value, it just plots the data

'''
def plot_E_RSI(data, overbought=70, oversold=30):
    
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    ax1.plot(data['Close'], label='Close')
    ax1.legend()
    ax1.grid()

    ax2.plot(data['E_RSI'], label='Exponential RSI')

    plt.fill_between(data.index, data['E_RSI'], where=(data['E_RSI'] < oversold), alpha=0.25, label='Oversold', color='green')
    plt.fill_between(data.index, data['E_RSI'], where=(data['E_RSI'] > overbought), alpha=0.25, label='Overbought', color='red')

    ax2.legend()
    ax2.set_title('Exponential RSI Indicator')
    plt.show()



'''
==== def MACD(data, longEMA, shortEMA, signalEMA) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> longEMA is the period for longer EMA
--> shortEMA is the period for shorter EMA
--> signalEMA is the period for signal line EMA
--> the functions return the same datafrane by adding columns for MACD, signal, Convergence/Divergence

'''
def MACD(data, longEMA=26, shortEMA=12, signalEMA=9):
    data['fast'] = data['Close'].ewm(span=shortEMA, adjust=False, min_periods=shortEMA).mean()
    data['slow'] = data['Close'].ewm(span=longEMA, adjust=False, min_periods=longEMA).mean()
    data['MACD'] = data['fast'] - data['slow']
    data['signal'] = data['MACD'].ewm(span=signalEMA, adjust=False, min_periods=signalEMA).mean()
    data['Convergence/Divergence'] = data['MACD'] - data['signal']
    data.drop(['fast', 'slow'], axis = 1, inplace=True)
    return data



'''
==== def plot_MACD(data) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly MACD, signal, Convergence/Divergence
--> the function has no return value, it just plots the data

'''
def plot_MACD(data):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    ax1.plot(data['Close'], label='Close')
    ax1.legend()
    ax1.grid()

    hist = data['Convergence/Divergence']
    for i in range(len(hist)):
        if hist[i] < 0:
            ax2.bar(hist.index[i], hist[i], color='red')
        if hist[i] > 0:
            ax2.bar(hist.index[i], hist[i], color='green')
        else:
            pass

    ax2.plot(data['MACD'], label='MACD')
    ax2.plot(data['signal'], label='Signal')
    ax2.legend()
    ax2.set_title('MACD Indicator')
    plt.show()



'''
==== def Money_Flow_Index(data, n) ==== 

--> data is the entire dataframe having Open, Low, High, Close, Volume
--> n is the period for MFI calculation
--> the functions return the same datafrane by adding columns for MFI

'''

def Money_Flow_Index(data, n=14):
    data['Positive_Flow']=0
    data['Negative_Flow']=0
    
    typical_price = (data['High']+data['Low']+data['Close'])/3
    money_flow = typical_price*data['Volume']
    positive_flow = data['Positive_Flow'].to_numpy()
    negative_flow = data['Negative_Flow'].to_numpy()
    
    for i in range(1, len(data.index)):
        if typical_price[i] > typical_price[i-1]:
            positive_flow[i] = money_flow[i]
            
        elif typical_price[i] < typical_price[i-1]:
            negative_flow[i] = money_flow[i]

    
    positive_sum = pd.Series(positive_flow).ewm(com=n-1, adjust=True, min_periods=n).mean()
    negative_sum = pd.Series(negative_flow).ewm(com=n-1, adjust=True, min_periods=n).mean()
    
    MFI = np.empty(positive_flow.shape)
    MF_Ratio = np.empty(positive_flow.shape)
    for i in range(0, len(data.index)):
        MF_Ratio[i] = positive_sum[i]/negative_sum[i]
        MFI[i] = 100-(100/(1+MF_Ratio[i]))
    
    
    data['MFI'] = MFI
    data.drop(['Positive_Flow', 'Negative_Flow'], axis = 1, inplace=True)
    return data




'''
==== def plot_MFI(data, overbought, oversold) ==== 

--> data is the entire dataframe having not just [O,L,H,C,V] columns but more importantly the MFI value column
--> the function has no return value, it just plots the data

'''
def plot_MFI(data, overbought=80, oversold=20):
    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, sharex=True)
    ax1.plot(data['Close'], label='Close')
    ax1.legend()
    ax1.grid()

    ax2.plot(data['MFI'], label='Money Flow Index', color='indigo')

    plt.fill_between(data.index, data['MFI'], where=(data['MFI'] < oversold), alpha=0.25, label='Oversold', color='green')
    plt.fill_between(data.index, data['MFI'], where=(data['MFI'] > overbought), alpha=0.25, label='Overbought', color='red')

    ax2.legend()
    ax2.set_title('Money Flow Index')
    plt.show()