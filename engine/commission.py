# -*- coding: utf-8 -*-

"""
Commission Model, including brokerage and tax

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""

import math
from abc import ABCMeta, abstractmethod


class Commission(object):
    """
    Commission abstract base class
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_commission(self, *args):
        raise NotImplementedError('function get_commission() is nor implemented!')


class ZeroCommission(Commission):
    """
    Zero commission model
    """

    def get_commission(self):
        return 0.0

    def __str__(self):
        return '{class_name}'.format(class_name=self.__class__.__name__)


class PerShareCommission(Commission):
    """
    Calculate the commission based on share amount
    """

    def __init__(self, rate=0.001, min_comm=0.0):
        self.rate_per_share = float(rate)
        self.min_comm = float(min_comm)

    def get_commission(self, quantity):
        return max(math.ceil(quantity * self.rate_per_share), self.min_comm)

    def __repr__(self):
        return '{class_name} {{rate_per_share={rate}, min_commission={min_comm}}'.format(
            class_name=self.__class__.__name__, rate=self.rate_per_share, min_comm=self.min_comm
        )


class PerMoneyCommission(Commission):
    """
    Commission model based on trade cost
    Trade cost may be future points or RMB
    There is a minimal setting in commission
    eg,
    """

    def __init__(self, rate=2.0e-4, min_comm=0.0):
        """
        Constructor
        :param rate:
        :param min_comm:
        """
        self.rate_per_money = float(rate)
        self.min_comm = float(min_comm)

    def get_commission(self, full_cost):
        return max(full_cost * self.rate_per_money, self.min_comm)

    def __repr__(self):
        return "{class_name}(rate_per_money={rate}, min_commission={min_comm})".format(
            class_name=self.__class__.__name__, rate=self.rate_per_money, min_comm=self.min_comm)


class PerTradeCommission(Commission):
    """
    Commission model based on trade times
    基于交易次数计算手续费
    """

    def get_commission(self):
        pass
