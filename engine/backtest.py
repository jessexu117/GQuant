# -*- coding: utf-8 -*-

"""
Main API for back-testing

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""

import time
import queue
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn

from .constant import EVENT_TICK, EVENT_BAR, EVENT_SIGNAL, EVENT_ORDER, EVENT_FILL, EMPTY_STRING
from .event import SignalEvent
from ..utils.logger import simple_logger

seaborn.set_style('whitegrid')
logger = simple_logger()


class Backtest(object):
    """
    Encapsulation of back-testing setting and module
    """

    def __init__(self, data_dir, symbol_list, initial_capital,
                 heartbeat, start_date, end_date, data_handler,
                 execution_handler, portfolio_handler, strategy,
                 commission_type='default', slippage_type='fixed',
                 **kwargs):
        """
        Initial Setting for Back-testing
        :param data_dir:
        :param symbol_list:
        :param initial_capital:
        :param heartbeat:
        :param start_date:
        :param end_date:
        :param data_handler:
        :param execution_handler:
        :param portfolio_handler:
        :param strategy:
        :param commission_type:
        :param slippage_type:
        :param kwargs: strategy parameter dictionary
        """
        self.data_dir = data_dir
        self.symbol_list = symbol_list
        self.initial_capital = initial_capital
        self.heartbeat = heartbeat
        self.start_date = start_date
        self.end_date = end_date

        self.data_handler_cls = data_handler
        self.execution_handler_cls = execution_handler
        self.portfolio_handler_cls = portfolio_handler
        self.strategy_cls = strategy

        self.commission_type = commission_type
        self.slippage_type = slippage_type

        self.events = queue.Queue()

        self.kwargs = kwargs

        self.signals = 0
        self.orders = 0
        self.fills = 0

        self.lst_bar_date = EMPTY_STRING

        self._generate_trading_instances()

    def _generate_trading_instances(self):
        """
        Generate an Instance of Backtest Class
        Get data_handler, strategy, portfolio_handler, execution_handler object
        :return:
        """
        self.data_handler = self.data_handler_cls(self.events, self.symbol_list,
                                                  self.start_date, self.end_date, self.data_dir)
        self.portfolio_handler = self.portfolio_handler_cls(self.data_handler, self.events,
                                                            self.start_date, self.initial_capital)
        self.execution_handler = self.execution_handler_cls(self.data_handler, self.events,
                                                            slippage_type=self.slippage_type,
                                                            commission_type=self.commission_type)
        self.strategy = self.strategy_cls(self.data_handler, self.portfolio_handler, self.events, **self.kwargs)

    def _run_backtest(self):
        """
        Run backtest
        :return:
        """
        # TODO: TICK TYPE + calculate_signals
        while True:
            # update bars
            bars = self.data_handler
            if bars.continue_backtest:
                bars.update_bars()
            else:
                break

            # time.sleep(self.heartbeat)
            # handle events
            while True:
                try:
                    event = self.events.get(block=False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.type == EVENT_TICK:
                            # TODO: TICK IMPLEMENT
                            pass

                        elif event.type == EVENT_BAR:
                            logger.debug(' '.join([event.bar[0], event.bar[1].strftime('%Y-%m-%d %H:%M:%S'),
                                                   str(event.bar[5])]))  # symbol, datetime, close
                            if event.bar[1].strftime('%Y-%m-%d') != self.lst_bar_date:
                                self.lst_bar_date = event.bar[1].strftime('%Y-%m-%d')
                                self.strategy.before_trading(event)

                            self.strategy.calculate_signals(event)
                            self.portfolio_handler.update_time_index()

                        elif event.type == EVENT_SIGNAL:
                            logger.info(' '.join(['Create Signal:', event.datetime.strftime('%Y-%m-%d %H:%M:%S'),
                                                  event.symbol, event.signal_type]))
                            self.signals += 1
                            self.portfolio_handler.update_signal(event)

                        elif event.type == EVENT_ORDER:
                            self.orders += 1
                            self.execution_handler.execute_order(event)

                        elif event.type == EVENT_FILL:
                            self.fills += 1
                            self.portfolio_handler.update_fill(event)

    def _force_close(self):
        """
        Force to close position when backtest is over
        :return:
        """
        for s in self.symbol_list:
            self.portfolio_handler.update_signal(SignalEvent(s, self.portfolio_handler.current_datetime, 'EXIT'))
            event = self.events.get()
            if event is not None:
                assert event.type == EVENT_ORDER
                self.execution_handler.execute_order(event)
                event = self.events.get()
                assert event.type == EVENT_FILL
                self.portfolio_handler.update_fill(event)
                self.portfolio_handler.update_time_index()
                logger.info(
                    ' '.join(['Force Clear:', self.portfolio_handler.current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                              s, 'EXIT']))

    @staticmethod
    def _output_performance(total_series, periods=252 * 4 * 60):
        """
        Print the performance of backtest
        including Money Curve, Sharpe ratio and Max-drawdown
        :param total_series: Account Money series
        :param periods: backtest time scale, period = 252 (day) or 252*24*60 (minute)
        """
        perform = total_series.to_frame(name='total')
        perform['return'] = perform['total'].pct_change()
        perform['curve'] = (1.0 + perform['return']).cumprod()
        ret = perform['curve'][-1] - 1
        sharpe_ratio = np.sqrt(periods) * np.mean(perform['return']) / np.std(perform['return'])

        perform['cum_max'] = perform['curve'].cummax()
        perform['drawdown'] = perform['curve'] / perform['cum_max'] - 1
        max_dd = perform['drawdown'].min()

        print('Return Rate: {}'.format(ret))
        print('Sharpe Ratio: {}'.format(sharpe_ratio))
        print('Maximal Drawdown: {}'.format(max_dd))

    @staticmethod
    def _plot_curve(total_series):
        """
        Plot the money curve
        :param total_series: Account Money series
        """
        curve = total_series.to_frame('total')
        curve['return'] = curve['total'].pct_change()
        curve['curve'] = (1.0 + curve['return']).cumprod()

        plt.figure(figsize=(15, 5))
        plt.plot(curve['total'], lw=0.7)
        plt.xlabel('datetime')
        plt.ylabel('return')
        plt.title('Curve')
        plt.grid(True)
        plt.show()

    @staticmethod
    def _plot_curve_min(money_list):
        """

        :param money_list:
        :return:
        """
        plt.figure(figsize=(15, 5))
        plt.plot(money_list)
        # plt.xlabel('datetime')
        plt.ylabel('return')
        plt.title('Curve')
        plt.grid(True)
        plt.show()

    def trade_record(self):
        """
        Get the trading record
        :return: a trading info record
        """
        trades = pd.DataFrame(self.portfolio_handler.all_trades,
                              columns=['datetime', 'exchange', 'symbol', 'direction',
                                       'fill_price', 'quantity', 'commission'])
        return trades.set_index('datetime')

    def simulate_trading(self):
        """
        Implement simulation and print backtest outcome
        including the money curve and position DataFrame
        :return:
        """
        start = time.time()
        logger.info('Start Backtest...')
        self._run_backtest()
        logger.info('Summary: Signals (%s), Orders (%s), Fills (%s)' % (self.signals, self.orders, self.fills))
        self._force_close()
        end = time.time()
        timing = round(end - start, 2)
        logger.info('Backtest took %s seconds!' % timing)

        positions = pd.DataFrame(self.portfolio_handler.all_positions).drop_duplicates(subset='datetime', keep='last'
                                                                                       ).set_index('datetime')
        holdings = pd.DataFrame(self.portfolio_handler.all_holdings).drop_duplicates(subset='datetime',
                                                                                     keep='last').set_index('datetime')

        Backtest._output_performance(total_series=holdings['total'])

        Backtest._plot_curve(total_series=holdings['total'])
        # Backtest._plot_curve_min(money_list=self.portfolio_handler.money_day_list)

        return positions, holdings
