# -*- coding: utf-8 -*-

"""
Portfolio Class
Achieve including: position track, order management, profile analysis and risk management

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""

from abc import ABCMeta, abstractmethod
from .constant import EVENT_FILL, EVENT_SIGNAL, ORDER_BUY, ORDER_SELL
from .constant import SIGNAL_LONG, SIGNAL_SHORT, SIGNAL_EXIT
from .event import OrderEvent


class PortfolioHandler(object):
    """
    Portfolio Abstract Base Class
    Abstract methods include: update position and holding market value
    Now it only can calculate by Bar, including second, 1min, 5min, 30min, 60min and etc.
    """
    # TODO: Tick Implement

    __metaclass__ = ABCMeta

    @abstractmethod
    def update_time_index(self):
        """
        For tracking updating holdings
        :return:
        """
        raise NotImplementedError('function update_time_index() is nor implemented!')

    @abstractmethod
    def update_signal(self, event):
        """
        Generate new orders from SignalEvent based on Portfolio Management
        :param event: SignalEvent
        :return:
        """
        raise NotImplementedError('function update_signal() is nor implemented!')

    @abstractmethod
    def update_fill(self, event):
        """
        Update position and holding market value from FillEvent
        :param event: FillEvent
        :return:
        """
        raise NotImplementedError('function update_fill() is nor implemented!')


class BasicPortfolioHandler(PortfolioHandler):
    """
    A Basic Portfolio Order Management Class
    BasicPortfolio sends orders to Brokerage object
    """

    # TODO: Risk Management or Position Management

    def __init__(self, bars, events, start_date, initial_capital=1.0e5):
        """
        Portfolio Initial Setting using Bars and Events Queue, including start date and initial capital
        :param bars: DataHandler object, current market data
        :param events: Event Queue object
        :param start_date: Portfolio start time
        :param initial_capital: Initial Capital
        """
        self.bars = bars
        self.events = events
        self.symbol_list = self.bars.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        self.current_datetime = start_date

        # TODO: LIST
        self.all_positions = self._construct_all_positions()  # dictionary list
        self.current_positions = {s: 0 for s in self.symbol_list}  # dictionary

        self.all_holdings = self._construct_all_holdings()  # dictionary list
        self.current_holdings = self._construct_current_holdings()  # dictionary

        self.all_trades = []
        self.money_day_list = [self.initial_capital]

    def _construct_all_positions(self):
        """
        Construct position list, its element is dictionary - key: symbol value: 0
        Add extra datetime key
        :return: position list
        """
        d = {s: 0 for s in self.symbol_list}
        d['datetime'] = self.start_date

        return [d]

    def _construct_all_holdings(self):
        """
        Construct all the holding market value
        including cash, accumulated commission and total value
        :return:
        """
        d = {s: 0 for s in self.symbol_list}
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        return [d]

    def _construct_current_holdings(self):
        """
        Construct the current holdings market value
        The difference from _construct_all_holdings() is only that it returns dictionary, not dictionary list
        :return:
        """
        d = {s: 0 for s in self.symbol_list}
        d['datetime'] = self.start_date
        d['cash'] = self.initial_capital
        d['commission'] = 0.0
        d['total'] = self.initial_capital

        return d

    def update_time_index(self):
        """
        Track the new holding market value
        Add new record into holdings
        get BarEvent from events queue
        :return:
        """
        bars = {}

        for sym in self.symbol_list:
            bars[sym] = self.bars.get_latest_bars(sym, n=1)

        self.current_datetime = bars[self.symbol_list[0]][0][1]

        # update positions - dictionary
        dp = {s: 0 for s in self.symbol_list}
        dp['datetime'] = self.current_datetime

        for s in self.symbol_list:
            dp[s] = self.current_positions[s]

        # add current position
        self.all_positions.append(dp)  # all_positions is k bar cycle dictionary list

        # update holdings - dictionary
        dh = {s: 0 for s in self.symbol_list}
        dh['datetime'] = self.current_datetime
        dh['cash'] = self.current_holdings['cash']
        dh['commission'] = self.current_holdings['commission']
        dh['total'] = self.current_holdings['cash']
        for s in self.symbol_list:
            # estimate holdings market value
            market_value = self.current_positions[s] * bars[s][0][5]
            dh[s] = market_value
            dh['total'] += market_value

        self.all_holdings.append(dh)

    # (1) Interactive with FillEvent object
    # Achieve update_fill() via three below tool functions

    def update_positions_from_fill(self, fill):
        """
        Update positions from FillEvent object
        :param fill: FillEvent object
        :return:
        """
        assert fill.direction in [ORDER_BUY, ORDER_SELL], AssertionError('fill direction error!')
        fill_dir = 1 if fill.direction == ORDER_BUY else -1

        self.current_positions[fill.symbol] += fill_dir * fill.quantity

    def update_holdings_from_fill(self, fill):
        """
        Update holdings from FillEvent object
        :param fill: FillEvent object
        :return:
        """
        assert fill.direction in [ORDER_BUY, ORDER_SELL], AssertionError('fill direction error!')
        fill_dir = 1 if fill.direction == ORDER_BUY else -1

        # fill_price = self.bars.get_latest_bars(fill.symbol)[0][5]  # close price
        fill_price = fill.fill_price
        cost = fill_dir * fill_price * fill.quantity

        self.current_holdings[fill.symbol] += cost
        self.current_holdings['commission'] += fill.commission
        self.current_holdings['cash'] -= (cost + fill.commission)
        self.current_holdings['total'] -= fill.commission

    def update_trades_from_fill(self, fill):
        """
        Update trade record from FillEvent object
        :param fill: FillEvent object
        :return:
        """
        current_trade = dict()
        current_trade['datetime'] = fill.time_index
        current_trade['symbol'] = fill.symbol
        current_trade['exchange'] = fill.exchange
        current_trade['quantity'] = fill.quantity
        current_trade['direction'] = fill.direction
        current_trade['fill_price'] = fill.fill_price
        current_trade['commission'] = fill.commission

        self.all_trades.append(current_trade)

    def update_fill(self, event):
        """
        Update portfolio positions and holdings from FillEvent object
        :param event: FillEvent object
        """
        if event.type == EVENT_FILL:
            self.update_positions_from_fill(event)
            self.update_holdings_from_fill(event)
            self.update_trades_from_fill(event)

    # (2) Interactive with SignalEvent object
    # Achieve update_signal() via a tool function: _generate_order()

    def _generate_naive_order(self, signal):
        # TODO: the transferring from signal event to order event is too naive
        # TODO: add risk management
        # TODO: order_type = 'LTD'
        """

        :param signal: SignalEvent
        :return: OrderEvent object
        """
        order = None

        symbol = signal.symbol
        direction = signal.signal_type
        mkt_quantity = 1  # future lot

        cur_quantity = self.current_positions[symbol]
        order_type = 'MKT'

        if cur_quantity == 0:
            if direction == SIGNAL_LONG:
                order = OrderEvent(symbol, order_type, mkt_quantity, ORDER_BUY)  # 开多仓
            elif direction == SIGNAL_SHORT:
                order = OrderEvent(symbol, order_type, mkt_quantity, ORDER_SELL)  # 开空仓
        elif cur_quantity > 0:
            if direction == SIGNAL_SHORT:
                order = OrderEvent(symbol, order_type, 2 * mkt_quantity, ORDER_SELL)  # 多翻空
            elif direction == SIGNAL_EXIT:
                order = OrderEvent(symbol, order_type, mkt_quantity, ORDER_SELL)  # 平多仓
        elif cur_quantity < 0:
            if direction == SIGNAL_LONG:
                order = OrderEvent(symbol, order_type, 2 * mkt_quantity, ORDER_BUY)  # 空翻多
            elif direction == SIGNAL_EXIT:
                order = OrderEvent(symbol, order_type, mkt_quantity, ORDER_BUY)  # 平空仓
        else:
            order = None

        return order

    def update_signal(self, event):
        """
        Generate new orders via SignalEvent object
        :param event: SignalEvent object
        """
        if event.type == EVENT_SIGNAL:
            order_event = self._generate_naive_order(event)
            self.events.put(order_event)
