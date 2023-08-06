from setuptools import setup, find_packages
import codecs

VERSION = '0.0.1'
DESCRIPTION = 'techfin : A package for technical analysis'
LONG_DESCRIPTION = '''A package that implements technical indicators and plotting functions of them

# Indicators implemented in the package

1. Simple Moving Average
2. Exponential Moving Average
3. Bollinger Bands
4. Simple Relative Strength Index
5. Exponential Relative Strength Index
6. Moving Average Convergence Divergence
7. Money Flow Index


## Installation

- Make sure you have numpy, pandas, yfinance, matplotlib installed

- Run Following command to install the package
```
  pip install techfin
```

## How to import

- Run Following command to import
```
  import techfin

  # The following packages are also necessary
  import pandas as pd
  import numpy as np
  import yfinance as yf
  import matplotlib.pylot as plt
```

## Example

```
  data = yf.download('HDFC.NS', start=2021-01-01, end=2022-01-01, interval='1d', auto_adjust=True)
  
  techfin.plot_Close(data)        # to plot close price of data
  
  n = [10, 50, 100]
  data_SMA = techfin.SMA(data, n) # to calulate simple moving average
  techfin.plot_SMA(data_SMA, n)   # to plot Simple moving average on the Close price graph

```



## List of Functions

| Sr. | Function                                   | Discription                                                    |
| --- | -------------------------------------------|----------------------------------------------------------------|
| 1.  | plot_Close (data)                          | Plot Close Price                                               |
| 2.  | SMA (data, n)                              | Calculate Simple Moving Average                                |
| 3.  | plot_SMA (data, n)                         | Plot Simple Moving Average                                     |
| 4.  | EMA (data, n)                              | Calculate Exponential Moving Average                           |
| 5.  | plot_EMA (data)                            | Plot Exponential Moving Average                                |
| 6.  | BollingerBands (data, n, factor)           | Calculate Bollinger Bands                                      |
| 7.  | plot_BollingerBands (data)                 | Plot Bollinger Bands                                           |
| 8.  | Simple_RSI (data, n)                       | Calculate Simple RSI                                           |
| 9.  | plot_S_RSI (data, overbought, oversold)    | Plot Simple RSI, highlighting overbought & oversold zones      |
| 10. | Exponential_RSI (data, n)                  | Calculate Exponential RSI                                      |
| 11. | plot_E_RSI (data, overbought, oversold)    | Plot Exponential RSI, highlighting overbought & oversold zones |
| 12. | MACD (data, longEMA, shortEMA, signalEMA)  | Calculate MACD indicator                                       |
| 13. | plot_MACD (data)                           | Plot MACD indicator along with bars for Convergence/Divergence |
| 14. | Money_Flow_Index (data, n)                 | Calculate Money Flow Index                                     |
| 15. | plot_MFI (data, overbought, oversold)      | Plot MFI, highlighting overbought & oversold zones             |

'''


setup(
    name="techfin",
    version=VERSION,
    author="UTKARSH SAHAYA",
    author_email="sahai.utkarsh@gmail.com",
    url = 'https://github.com/ut-upwards/techfin',
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=['techfin'],
    install_requires=['pandas', 'numpy', 'matplotlib', 'yfinance'],
    keywords=['techical-analysis', 'finance', 'tech_fin', 'indicators', 'RSI', 'MACD', 'MFI', 'Moving Average'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)