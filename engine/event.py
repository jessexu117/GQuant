# -*- coding: utf-8 -*-

"""
Event Class
Event can be transfer between data, portfolio and simulated exchange

@author: Jesse J. Hsu
@email: jinjie.xu@whu.edu.cn
@version: 0.1
"""

from abc import ABCMeta
from .constant import EVENT_TICK, EVENT_BAR, EVENT_SIGNAL, EVENT_ORDER, EVENT_FILL


class Event(object):
    """
    Event abstract base class
    Just for inheritance, subclass including Tick, Bar, Signal, Order and Fill
    """
    __metaclass__ = ABCMeta


class TickEvent(Event):
    """

    """

    def __init__(self, tick):
        self.type = EVENT_TICK
        self.tick = tick

    def __str__(self):
        format_tick = 'Type: %s, Symbol: %s, Datetime: %s, Bid: %s, Ask: %s' % (
            self.type, self.tick[0], self.tick[1], self.tick[2], self.tick[3]
        )
        return format_tick

    # __repr__ = __str__
    def __repr__(self):
        return str(self)


class BarEvent(Event):
    """
    Bar event class (basic market data)
    """

    def __init__(self, bar):
        """
        Constructor
        :param bar: a tuple type standard OHLCV
        """
        self.type = EVENT_BAR
        self.bar = bar

    def __str__(self):
        format_bar = 'Type: %s, Symbol: %s, Datetime: %s, ' \
                     'Open: %s, High: %s, Low: %s, Close: %s, Volume: %s' % (
                         self.type, self.bar[0], self.bar[1],
                         self.bar[2], self.bar[3], self.bar[4], self.bar[5], self.bar[6]
                     )
        return format_bar

    def __repr__(self):
        return str(self)


class SignalEvent(Event):
    """
    Signal event class
    Procedure: Strategy object send signal, and received by Portfolio object
    """

    def __init__(self, symbol, datetime, signal_type, strategy_id=1, strength=1.0):
        """
        Constructor
        :param symbol:
        :param datetime:
        :param signal_type:
        :param strategy_id:
        :param strength:
        """
        self.type = EVENT_SIGNAL
        self.symbol = symbol
        self.datetime = datetime
        self.signal_type = signal_type
        self.strategy_id = strategy_id
        self.strength = strength


class OrderEvent(Event):
    """
    Order event class
    Procedure: send a order to execution system
    """

    def __init__(self, symbol, order_type, quantity, direction):
        """
        Constructor
        :param symbol: symbol of future
        :param order_type: 'MKT' or 'LMT'
        :param quantity:
        :param direction: order direction, including BUY and SELL
        """
        self.type = EVENT_ORDER
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        """
        Print the value of order
        """
        print("Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
              (self.symbol, self.order_type, self.quantity, self.direction))


class FillEvent(Event):
    """
    Fill event class
    Fill or Kill (FOK order), fill all or cancel all
    """

    def __init__(self, time_index, symbol, exchange, quantity, direction,
                 fill_price, commission):
        """
        Constructor, order deal information
        :param time_index: the time index of the fill bar
        :param symbol: deal future symbol
        :param exchange: exchange
        :param quantity: deal quantity
        :param direction: deal direction
        :param fill_price: deal price
        :param commission: fee
        """
        self.type = EVENT_FILL
        self.time_index = time_index
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction
        self.fill_price = fill_price
        self.commission = commission

