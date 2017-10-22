# GQuant

A Simple Event-driven Backtester for futures market with Python 3.x

Note: GQuant is a simple backtesting frame for Chinese Futures Market. Personally speaking, it's a efficient tool or project to understand the key idea of event-driven programming model and object-oriented programming with Python, and their application on quantitative development/financial computing. 

## Environment：

- Python >= 3.5
- Numpy
- Pandas
- Matplotlib

## Engine:

- **Commission model**, including zero commission model, per share commission model, per money commission model and per trade commission model.
- **Slippage model**, including zero slippage model, fixed percent slippage model and volume share slippage model.
- Data model, date handler.

## Improvement:

- More dedicated designed exchange simulator. It is flexible and extendible, for day/hour/minute/second/tick level data executor. Even you can make it for order book dynamics research.
- Maybe you's like to link with CTP or SimNow, and it's OKay.
- More accurate commission model for different financial trading underlying and  different markets. 
- More precise slippage model for different liqudity environment.
- Add risk management module in the Portfolio model.