# -*- coding: utf-8 -*-

"""
DataHandler Abstract Base Class

@author: Jesse J. Hsu
@email: jessexu117@outlook.com
@version: 0.1
"""
import os
import pandas as pd
from datetime import *
from abc import ABCMeta, abstractmethod
from collections import namedtuple

try:
    from WindPy import *
except ImportError:
    pass
else:
    w.start()
    w.isconnected()

from .event import BarEvent


class DataHandler(object):
    """
    DataHandler abstract base class, just for inheritance
    any inherited instance is used to make bar series (OHLCV) for every symbol
    There is no difference between historical and real-time data
    """
    Bar = namedtuple('Bar', ('symbol', 'datetime', 'open', 'high', 'low', 'close', 'volume'))

    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bars(self, symbol, n=1):
        """
        Get latest n bars from latest symbol list
        If available bar amount is less the n, them turn all the bars
        :param symbol: symbol of bar
        :param n: amount of bars
        """
        raise NotImplementedError('function get_latest_bars() is not implemented!')

    @abstractmethod
    def update_bars(self):
        """
        Update the bars
        """
        raise NotImplementedError('function update_bars() is not implemented!')


class CSVDataHandler(DataHandler):
    """
    Data handler via csv file
    CSV file can be normalized generated via VBA and Data API
    """

    def __init__(self, events, symbol_list, start_date, end_date, dir):
        """
        Constructor
        :param events: queue
        :param symbol_list:
        :param start_date:
        :param end_date:
        """
        self.events = events
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date
        self.csv_dir = dir

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_csv_files()

    def _open_convert_csv_files(self):
        """
        Open csv file from data directory and transfer into DataFrames
        Column index: 'datetime'(increasing sort), 'open', 'high', 'low', 'close', 'volume'
        Row index:
        """
        comb_index = None
        for s in self.symbol_list:
            self.symbol_data[s] = pd.read_csv(
                os.path.join(self.csv_dir, '%s.csv' % s),
                header=0, index_col=0, parse_dates=True,
                names=['datetime', 'open', 'high', 'low', 'close', 'volume']
            ).dropna().sort_index()[self.start_date:self.end_date]

            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def get_bar(self, symbol, _date):
        """

        :param symbol:
        :param _date:
        :return:
        """
        pass

    def get_bars(self, symbol, date1, date2):
        """

        :param symbol:
        :param date1:
        :param date2:
        :return:
        """
        pass

    def _get_new_bar(self, symbol):
        """
        Get the latest bar, format is (symbol, datetime, open, high, low, close, volume)
        Generator: generate a new bar at each call, until it come to end of data
        Called in update_bars()
        """
        for b in self.symbol_data[symbol]:
            yield DataHandler.Bar(symbol, b[0], b[1][0], b[1][1], b[1][2], b[1][3], b[1][4])

    def get_latest_bars(self, symbol, n=1):
        """

        :param symbol:
        :param n:
        :return:
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar_list[-n:]

    def get_latest_bar(self, symbol):
        """

        :param symbol:
        :return:
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar_list[-1]

    def get_latest_bar_datetime(self, symbol):
        """

        :param symbol:
        :return:
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bars_list[-1][1]

    def update_bars(self):
        """

        :return:
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
                    self.events.put(BarEvent(bar))


class DBDataHandler(DataHandler):
    """
    Data handler via database
    """

    def __init__(self, events, symbol_list, start_date, end_date, *args):
        """
        Constructor
        :param events:
        :param db_dir:
        :param symbol_list:
        :param start_date:
        :param end_date:
        """
        self.events = events
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date
        self.db_dir = args

        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._open_convert_database()

    def _open_convert_database(self):
        """
        Get data from
        :return:
        """
        pass

    def get_bar(self, symbol, _date):
        """

        :param symbol:
        :param _date:
        :return:
        """
        pass

    def get_bars(self, symbol, date1, date2):
        """

        :param symbol:
        :param date1:
        :param date2:
        :return:
        """
        pass

    def _get_new_bar(self, symbol):
        """

        :param symbol:
        :return:
        """
        pass

    def get_latest_bars(self, symbol, n=1):
        """

        :param symbol:
        :param n:
        :return:
        """
        pass

    def get_latest_bar(self, symbol):
        """

        :param symbol:
        :return:
        """
        pass

    def get_latest_bar_datetime(self, symbol):
        """

        :param symbol:
        :return:
        """
        pass

    def update_bars(self):
        """

        :return:
        """
        pass


class WindDataHandler(DataHandler):
    """
    Wind API DataHandler Class
    """

    def __init__(self, events, symbol_list, start_date, end_date, *args):
        """
        Constructor
        :param events: events queue
        :param symbol_list:
        :param start_date:
        :param end_date:
        """
        self.events = events
        self.symbol_list = symbol_list
        self.start_date = start_date
        self.end_date = end_date
        self.dir = args

        self.all_symbol_data = {}
        self.symbol_data = {}
        self.latest_symbol_data = {}
        self.continue_backtest = True

        self._convert_wind_data()

    def _convert_wind_data(self):
        """
        Open csv file from data directory and transfer into DataFrames
        Column index: 'datetime'(increasing sort), 'open', 'high', 'low', 'close', 'volume'
        Row index:
        """
        comb_index = None
        date1 = self.start_date
        trading_date_list = w.tdays(self.start_date - timedelta(days=20), self.end_date).Data[0]
        try:
            date1 = trading_date_list[trading_date_list.index(self.start_date) - 1]
        except KeyError:
            print('Please input trading date format for start date!')

        for s in self.symbol_list:
            w_wsi_data = w.wsi(s, "open,high,low,close,volume", date1, self.end_date)
            sym_data = pd.DataFrame()
            sym_data['datetime'] = w_wsi_data.Times
            for i, index in enumerate(['open', 'high', 'low', 'close', 'volume']):
                sym_data[index] = w_wsi_data.Data[i]

            self.all_symbol_data[s] = sym_data.dropna().set_index('datetime').sort_index()[self.start_date:self.end_date]
            self.symbol_data[s] = sym_data.dropna().set_index('datetime').sort_index()[self.start_date:self.end_date]
            print(self.all_symbol_data[s])
            if comb_index is None:
                comb_index = self.symbol_data[s].index
            else:
                comb_index.union(self.symbol_data[s].index)
            self.latest_symbol_data[s] = []

        for s in self.symbol_list:
            self.symbol_data[s] = self.symbol_data[s].reindex(index=comb_index, method='pad').iterrows()

    def _get_new_bar(self, symbol):
        """
        Get the latest bar, format is (symbol, datetime, open, high, low, close, volume)
        Generator: generate a new bar at each call, until it come to end of data
        Called in update_bars()
        """
        for b in self.symbol_data[symbol]:
            yield DataHandler.Bar(symbol, b[0], b[1][0], b[1][1], b[1][2], b[1][3], b[1][4])

    def get_bar(self, symbol, date1):
        """

        :param symbol:
        :param date1:
        :return:
        """
        try:
            bar = self.all_symbol_data[symbol][date1]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar

    def get_bars(self, symbol, date1, date2):
        """

        :param symbol:
        :param date1:
        :param date2:
        :return:
        """
        try:
            bar_list = self.all_symbol_data[symbol][date1:date2]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar_list

    def get_latest_bars(self, symbol, n=1):
        """

        :param symbol:
        :param n:
        :return:
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar_list[-n:]

    def get_latest_bar(self, symbol):
        """

        :param symbol:
        :return:
        """
        try:
            bar_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bar_list[-1]

    def get_latest_bar_datetime(self, symbol):
        """

        :param symbol:
        :return:
        """
        try:
            bars_list = self.latest_symbol_data[symbol]
        except KeyError:
            print("Not available symbol in the historical data set!")
        else:
            return bars_list[-1][1]

    def update_bars(self):
        """

        :return:
        """
        for s in self.symbol_list:
            try:
                bar = next(self._get_new_bar(s))
            except StopIteration:
                self.continue_backtest = False
            else:
                if bar is not None:
                    self.latest_symbol_data[s].append(bar)
                    self.events.put(BarEvent(bar))


class RealTimeDataHandler(DataHandler):
    """
    Real-time DataHandler Class
    """

    def __init__(self):
        pass

    def get_latest_bars(self, symbol, n=1):
        pass

    def update_bars(self):
        pass
