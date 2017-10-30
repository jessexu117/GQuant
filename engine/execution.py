# -*- coding: utf-8 -*-

"""
ExecutionHandler Class
Order Execution Simulation in Exchange

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""

from abc import ABCMeta, abstractmethod

from .constant import EVENT_ORDER
from .event import FillEvent
from .commission import ZeroCommission, PerMoneyCommission
from .slippage import ZeroSlippage, FixedPercentSlippage
from ..utils.symbol import get_exchange


class ExecutionHandler(object):
    """
    ExecutionHandler Abstract Base Class
    Handle the order from Portfolio object, and get the Fill object after deal
    Inherited sub class can be simulated exchange or the real live trading API
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event):
        """
        Get a order event, then execute and send a Fill event to Events queue
        :param event: an event with order information
        """
        raise NotImplementedError('function execute_order is nor implemented!')


class SimulatedExecutionHandler(ExecutionHandler):
    """
    A simple simulated exchange
    TODO: Consider partial fill, slippage and waiting time
    """

    def __init__(self, bars, events, slippage_type='fixed', commission_type='default'):
        """
        Constructor
        :param bars:
        :param events: Event queue
        :param slippage_type: slippage model, fixed or zero
        :param commission_type: commission model, zero or default
        """
        self.bars = bars
        self.events = events
        self.commission_type = commission_type
        self.slippage_type = slippage_type

        self.commission = 0.0

    def _trade_with_slippage(self, event):
        """
        Consider the fill price with slippage
        :param event: order event
        :return:
        """
        order_price = self.bars.get_latest_bars(event.symbol)[0][5]
        if self.slippage_type == 'zero':
            return ZeroSlippage().get_trade_price(order_price)
        elif self.slippage_type == 'fixed':
            fixed_slippage = FixedPercentSlippage(percent=0.1)
            return fixed_slippage.get_trade_price(order_price, event.direction)
        else:
            return order_price

    def _get_commission(self, event):
        """
        Calculate the commission of future
        :param event: order event
        :return: full commission
        """
        self.fill_price = self._trade_with_slippage(event)
        full_cost = self.fill_price * event.quantity

        if self.commission_type == 'zero':
            commission = ZeroCommission().get_commission()

        elif self.commission_type == 'default':
            if event.symbol.startswith('I'):  # Index Future
                commission = PerMoneyCommission(rate=3.0e-5).get_commission(full_cost)
            elif get_exchange(event.symbol) in ('SQ.EX', 'DS.EX', 'ZS.EX'):  # Commodity Future
                commission = PerMoneyCommission(rate=1.5e-4).get_commission(full_cost)
            else:
                commission = 0.0
        else:
            commission = 0.0

        return commission

    def execute_order(self, event):
        """
        Simple Execution: from Order object to Fill object
        :param event: event object containing order information
        """
        if event.type == EVENT_ORDER:
            self.commission = self._get_commission(event)
            assert isinstance(self.commission, float), 'Commission should be float!'
            time_index = self.bars.get_latest_bars(event.symbol)[0][1]
            fill_event = FillEvent(time_index, event.symbol, 'SimulatedExchange',
                                   event.quantity, event.direction, self.fill_price,
                                   self.commission)
            self.events.put(fill_event)


class CTPExecutionHandler(ExecutionHandler):
    """
    CTP Algorithmic Trading API Inheritance Class
    """

    def __init__(self):
        """
        Constructor
        """
        pass

    def execute_order(self, event):
        """

        :param event:
        :return:
        """
        pass
