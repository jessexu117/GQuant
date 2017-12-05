# -*- coding: utf-8 -*-

"""
R-Breaker Trading System

R-Breaker交易系统：
1.根据前一个交易日的收盘价、最高价和最低价数据通过一定方式计算出六个价位，从大到小依次为：突破买入价、观察卖出价、反转卖出价、反转买入价、观察买入价、突破卖出价。
　　以此来形成当前交易日盘中交易的触发条件。这里，通过对计算方式的调整，可以调节六个价格间的距离，进一步改变触发条件。
2. 追踪盘中价格走势，实时判断触发条件。具体条件如下：
    当日内最高价超过观察卖出价后，盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，采取反转策略，即在该点位（反手、开仓）做空；
    当日内最低价低于观察买入价后，盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，采取反转策略，即在该点位（反手、开仓）做多；
    在空仓的情况下，如果盘中价格超过突破买入价，则采取趋势策略，即在该点位开仓做多；
    在空仓的情况下，如果盘中价格跌破突破卖出价，则采取趋势策略，即在该点位开仓做空。
3. 设定止损条件。当亏损达到设定值后，平仓。
4. 设定过滤条件。当前一个交易日波幅过小，该交易日不进行交易。
5. 在每日收盘前，对所持合约进行平仓。不隔夜留仓。
6. 可使用1分钟、5分钟或10分钟等高频数据进行判断。

附加: 加入停止交易的机制。R-Breaker 策略只要在日内产生穿越信号就会开仓，有时即使上一个交易日震幅较大，6个价格之间距离较远，
    当日仍然会出现1分钟实时收盘价在某根价位线上下反复来回穿越的情形，导致在较小的区间内频繁开仓平仓，产生大量的交易成本。
"""

import os
from datetime import *

try:
    from WindPy import *
except ImportError:
    pass
else:
    w.start()
    w.isconnected()

from gquant import SignalEvent, Strategy, CSVDataHandler, SimulatedExecutionHandler, Backtest, BasicPortfolioHandler


class RBreaker(Strategy):
    """R-Breaker"""

    bsetup = 0.0
    ssetup = 0.0
    benter = 0.0
    senter = 0.0
    bbreak = 0.0
    sbreak = 0.0

    trading_today = True

    lst_dominant = []
    price_list = []
    trade_count = 0
    current_position = {}

    day_first_capital = 0.0

    def __init__(self, bars, portfolio, events):
        self.bars = bars
        self.symbol_list = self.bars.symbol_list
        self.portfolio = portfolio
        self.events = events

        self.future = self.bars.symbol_list[0]

        self.bought = {s: False for s in self.symbol_list}

        # strategy setting
        self.f1 = 0.35
        self.f2 = 0.07
        self.f3 = 0.25
        self.stop_loss_rate = -0.05
        self.swing_threshold = 0  # 前日波幅阈值
        self.lot = 1  # 开仓手数
        self.trade_per_day = 5  # 每天最多交易次数
        self.trend = True
        self.revert = False

        self._data_preprocessor()

    def _data_preprocessor(self):
        """
        
        :return: 
        """
        lst_date1 = self.bars.start_date - timedelta(days=1)
        lst_date2 = self.bars.end_date - timedelta(days=1)
        data = w.wsd(self.future, "close,high,low", lst_date1, lst_date2)

        self.close_lst = data.Data[0]
        self.high_lst = data.Data[1]
        self.low_lst = data.Data[2]

        self.day_first_capital = self.portfolio.current_holdings['total']

        self.current_position = {s: 0 for s in self.symbol_list}

    def _exit_position(self, bar):
        """

        :param bar:
        :return:
        """
        if not self.bought[self.future]:
            signal = SignalEvent(bar.symbol, bar.datetime, 'EXIT')
            self.events.put(signal)
            self.bought[self.future] = True

            return True

    def _long_position(self, bar):
        """

        :param bar:
        :return:
        """
        if not self.bought[self.future]:
            signal = SignalEvent(bar.symbol, bar.datetime, 'LONG')
            self.events.put(signal)
            self.bought[self.future] = True

            return True

    def _short_position(self, bar):
        """

        :param bar:
        :return:
        """
        if self.bought[self.future]:
            signal = SignalEvent(bar.symbol, bar.datetime, 'SHORT')
            self.events.put(signal)
            self.bought[self.future] = False

            return True

    def before_trading(self):
        """

        :return:
        """
        # 用于临时储存当天的价格序列
        self.price_list = []

        # 初始化每天交易次数
        self.trade_count = 0

        # 获取前一个交易日K线数据
        close = self.close_lst.pop(0)
        high = self.high_lst.pop(0)
        low = self.low_lst.pop(0)

        # 判断前日波幅
        self.trading_today = False if high - low < self.swing_threshold else True

        # 计算六个价位
        self.bsetup = low - self.f1 * (high - close)  # 观察买入价
        self.ssetup = high + self.f1 * (close - low)  # 观察卖出价
        self.benter = (1 + self.f2) / 2 * (high + low) - self.f2 * high  # 反转买入价
        self.senter = (1 + self.f2) / 2 * (high + low) - self.f2 * low  # 反转卖出价
        self.bbreak = self.ssetup + self.f3 * (self.ssetup - self.bsetup)  # 突破买入价
        self.sbreak = self.bsetup - self.f3 * (self.ssetup - self.bsetup)  # 突破卖出价

        # print('bbreak: ', self.bbreak)
        # print('ssetup: ', self.ssetup)
        # print('senter: ', self.senter)
        # print('benter: ', self.benter)
        # print('bsetup: ', self.bsetup)
        # print('sbreak: ', self.sbreak)
        # print(' ')

    def calculate_signals(self, event):
        """

        :param event:
        :return:
        """
        # print('event.bar: ', event.bar)
        # print('self.bars.get_latest_bar(): ', self.bars.get_latest_bar(self.future))
        bar = self.bars.get_latest_bar(self.future)

        # 设定过滤条件: 当前一个交易日波幅过小，该交易日不进行交易
        if not self.trading_today:
            return

        # 获取多头和空头持仓量
        position = self.current_position[self.future]
        # print('position1: ', self.current_position[self.future])
        # print('position2: ', self.portfolio.current_positions[self.future])
        # qty_buy = position.buy_quantity  # 多头持仓
        # qty_sell = position.sell_quantity  # 空头持仓

        # 判断是否盘中时间
        if bar[1].hour < 15:
            lst_price = bar[5]

            self.price_list.append(lst_price)
            day_high = max(self.price_list)
            day_low = min(self.price_list)

            # 判断是否空仓
            flat_condition = (position == 0)

            if self.trend:
                # 在空仓的情况下，如果盘中价格超过突破买入价，则采取趋势策略，即在该点位开仓做多
                if flat_condition and (lst_price > self.bbreak):
                    if self._long_position(bar):
                        print('趋势交易: 超过突破买入价，空仓做多')
                        self.trade_count += 1

                # 在空仓的情况下，如果盘中价格跌破突破卖出价，则采取趋势策略，即在该点位开仓做空
                elif flat_condition and (lst_price < self.sbreak):
                    if self._short_position(bar):
                        print('趋势交易: 跌破突破卖出价，空仓做空')
                        self.trade_count += 1

                elif not flat_condition and (lst_price < 0.98 * self.bbreak):
                    if self._exit_position(bar):
                        print('跌下突破买入价*0.98，平仓')
                        self.trade_count += 1

                elif not flat_condition and (lst_price > 0.98 * self.sbreak):
                    if self._exit_position(bar):
                        print('涨上突破卖出价*0.98，平仓')
                        self.trade_count += 1
            if self.revert:
                # 当日内最高价超过观察卖出价后，盘中价格出现回落，且进一步跌破反转卖出价构成的支撑线时，采取反转策略，即在该点位（反手、开仓）做空
                if day_high > self.ssetup and lst_price < self.senter and position > 0:
                    if self._short_position(bar):
                        print('反转交易: 跌破反转卖出价，多单做空')
                        self.trade_count += 1

                elif day_high > self.ssetup and lst_price < self.senter and position == 0:
                    if self._short_position(bar):
                        print('反转交易: 跌破反转卖出价，开仓做空')
                        self.trade_count += 1

                # 当日内最低价低于观察买入价后，盘中价格出现反弹，且进一步超过反转买入价构成的阻力线时，采取反转策略，即在该点位（反手、开仓）做多
                elif day_low < self.bsetup and lst_price > self.benter and position < 0:
                    if self._long_position(bar):
                        print('反转交易: 超过反转买入价，空单做多')
                        self.trade_count += 1

                elif day_low < self.bsetup and lst_price > self.benter and position == 0:
                    if self._long_position(bar):
                        print('反转交易: 超过反转买入价，开仓做多')
                        self.trade_count += 1

        # 在每日收盘前，对所持合约进行平仓
        elif bar[1].hour == 15:
            if self._exit_position(bar):
                print('收盘平仓！')

        # 如达到交易次数限制，则平仓然后今日不再交易
        if self.trade_count >= self.trade_per_day:
            if self._exit_position(bar):
                self.trading_today = False
                print('交易次数超出限制，强制平仓!')

        # 设定止损条件: 当亏损达到设定值后，平仓
        current_holdings = self.portfolio.current_holdings['total']

        if current_holdings / self.day_first_capital - 1 < self.stop_loss_rate:
            if self._exit_position(bar):
                print('止损')


if __name__ == '__main__':
    csv_dir = os.path.join(os.path.dirname(os.getcwd()), 'r-breaker')
    # print(csv_dir)
    symbol_list = ['RU.SHF']
    initial_capital = 100000.0
    heartbeat = 0.0
    start_date = datetime(2017, 1, 4, 0, 0)
    end_date = datetime(2017, 9, 1, 0, 0)

    backtest = Backtest(csv_dir, symbol_list, initial_capital, heartbeat,
                        start_date, end_date, CSVDataHandler, SimulatedExecutionHandler,
                        BasicPortfolioHandler, RBreaker,
                        slippage_type='fixed', commission_type='default')

    positions, holdings = backtest.simulate_trading()
    print(holdings)
