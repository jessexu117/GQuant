# -*- coding: utf-8 -*-

"""
Slippage Model

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""

from abc import ABCMeta, abstractmethod


class Slippage(object):
    """
    Slippage abstract base class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_trade_price(self, *args):
        raise NotImplementedError("function get_trade_price() is not implemented!")


class ZeroSlippage(Slippage):
    """
    Zero slippage model
    """

    def get_trade_price(self, price):
        return price


class FixedPercentSlippage(Slippage):
    """
    Slippage model with a fixed percent rate of price
    """

    def __init__(self, percent=0.0):
        """
        Constructor
        :param percent: slippage percent
        """
        self.rate = percent / 100.0

    def get_trade_price(self, price, direction):
        """
        Get the realized deal price with a slippage
        :param price: the price of signal
        :param direction: including BUY/SELL/SHORT/COVER
        :return: deal price
        """
        slippage = price * self.rate * (1 if direction == 'BUY' else -1)
        price = price + slippage

        return price


class VolumeShareSlippage(Slippage):
    """
    Slippage model with volume of share
    """

    def get_trade_price(self, price, direction):
        pass
