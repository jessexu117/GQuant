# GQuant

A Simple Event-driven Backtester for futures market with Python 3.x

Author: Jesse J. Hsu

Email: jinjie.xu@whu.edu.cn

**Note:** GQuant is a simple backtesting frame for Chinese Futures Market. Personally speaking, it's a efficient tool or project to understand the key idea of event-driven programming model and object-oriented programming with Python, and their application on quantitative development/financial computing. 

## Environment：

- Python >= 3.5
- Numpy
- Pandas
- Matplotlib

## Engine:

- **Commission model**, including zero commission model, per share commission model, per money commission model and per trade commission model.
- **Slippage model**, including zero slippage model, fixed percent slippage model and volume share slippage model.
- **Data model**, date handler. Including CSV data handler, Relational Database handler and Wind data handler. 
- **Execution model**, order execution simulation in exhcnage. The given simulator is a simple example.
- **Portfolio model**, position tracking, order management, profile analysis and risk management. There is a given basic portfolio model.
- **Event model**, event can be tranfered between data, portfolio and simulated exchange. including tick event, bar event, signal event, fill event etc.
- **Strategy model**, the strategy object calculates the market data, send signal to portfolio object.
- **Back-Test Class**, the main API for backtesting.

## Easy Strategy:

```python
# -*- coding: utf-8 -*-

import os
from datetime import *

from gquant import SignalEvent, Strategy, CSVDataHandler, SimulatedExecutionHandler, Backtest, BasicPortfolioHandler

class MyStrategy(Strategy):
    """
    My Strategy class
    """
    def __init__(self, bars, portfolio, events):
        pass

    def _data_preprocessor(self):
        pass

    def before_trading(self):
        pass

    def calculate_signals(self, event):
        pass

if __name__ == '__main__':
    csv_dir = os.path.join(os.path.dirname(os.getcwd()), 'mystrategy')
    start_date = datetime(2017, 1, 4, 0, 0)
    end_date = datetime(2017, 9, 1, 0, 0)
    backtest = Backtest(csv_dir, symbol_list=['RU.SHF'], initial_capital=10000.0, heartbeat=0.0,
                        start_date, end_date, CSVDataHandler, SimulatedExecutionHandler,
                        BasicPortfolioHandler, MyStrategy, slippage_type='fixed', commission_type='default')

    positions, holdings = backtest.simulate_trading()
    print(holdings)
```

## Plot:

![https://www.backtrader.com/static/images/sigsmacross2.png](https://www.backtrader.com/static/images/sigsmacross2.png)

## Improvement:

- More dedicated designed exchange simulator. It is flexible and extendible, for day/hour/minute/second/tick level data executor. Even you can make it for order book dynamics research.
- Maybe you's like to link with CTP or SimNow, and it's OKay.
- More accurate commission model for different financial trading underlying and  different markets. 
- More precise slippage model for different liqudity environment.
- Add risk management module in the Portfolio model.