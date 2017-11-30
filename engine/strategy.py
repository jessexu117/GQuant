# -*- coding: utf-8 -*-

"""
Strategy Class
The Strategy object calculates the market data, send signal to Portfolio object
Market data by DataHandler -> Strategy -> Signal for Portfolio

@author: Jesse J. Hsu
@email: jinjie.xu@whu.edu.cn
@version: 0.1 
"""

import pandas as pd
from abc import ABCMeta, abstractmethod

from .event import SignalEvent


class Strategy(object):
    """
    Strategy abstract base class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def before_trading(self, event):
        """

        :return:
        """
        raise NotImplementedError('function before_trading() is not implemented!')

    @abstractmethod
    def calculate_signals(self, event):
        """
        Offer the procedure of calculating signal
        """
        raise NotImplementedError('function calculate_signals() is not implemented!')


# example strategy：golden cross
class MovingAverageCrossStrategy(Strategy):
    """
    移动双均线策略
    """

    def __init__(self, bars, events, long_window=10, short_window=5):
        """
        初始化移动双均线策略
        参数：
        bars：DataHandler类的对象，属性和方法可以具体参考data模块
        events: Event对象
        """
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.events = events
        self.long_window = long_window  # long tern MA
        self.short_window = short_window  # short term MA

        self.bought = self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        """
        添加key到bought字典，将所有股票的值设为False，意指尚未持有
        TODO：是否可以用组合中虚拟账户来监控，strategy只管发信号呢？
        """
        bought = {}
        for s in self.symbol_list:
            bought[s] = False
        return bought

    def before_trading(self, event):
        """

        :return:
        """
        pass

    def calculate_signals(self, event):
        """
        当短期均线（如5日线）上穿长期均线（如10日线），买入
        反之，卖出；不做空
        """
        if event.type == 'MARKET':
            for s in self.symbol_list:
                bars = self.bars.get_latest_bars(s, N=self.long_window)  # 元组的列表
                if bars is not None and bars != [] and len(bars) >= self.long_window:
                    # 转换成DataFrame计算，代码量少一些，暂不考虑速度
                    cols = ['symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume']
                    df = pd.DataFrame(bars, columns=cols)
                    df['MA_long'] = df['close'].rolling(center=False, window=self.long_window, min_periods=1).mean()
                    df['MA_short'] = df['close'].rolling(center=False, window=self.short_window,
                                                         min_periods=1).mean()
                    if df['MA_long'].iloc[-1] < df['MA_short'].iloc[-1] and df['MA_long'].iloc[-2] \
                            > df['MA_short'].iloc[-2] and not self.bought[s]:
                        signal = SignalEvent(bars[-1][0], bars[-1][1], 'LONG')
                        self.events.put(signal)
                        self.bought[s] = True

                    elif df['MA_long'].iloc[-1] > df['MA_short'].iloc[-1] and df['MA_long'].iloc[-2] \
                            < df['MA_short'].iloc[-2] and self.bought[s]:
                        signal = SignalEvent(bars[-1][0], bars[-1][1], 'EXIT')
                        self.events.put(signal)
                        self.bought[s] = False
