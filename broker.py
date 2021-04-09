from accessor import *
from order import Order
from copy import deepcopy
import pandas as pd
import numpy as np
import util


class Broker:
    def __init__(self, equity):

        self.execute = Execute(equity)  # Execute

    def make_order(self, unit, limit_price, stop_loss, stop_profit):

        order_queue.append(Order(unit, limit_price, stop_loss, stop_profit))

    def check_order(self, ohlc, date, commission):
        """
        check the order and set the information to order by different condition
        """

        op = ohlc[0]

        for o in order_queue:
            if position() != 0 and position() + o.units != 0 and len(order_queue) == 1:
                o.is_parents = False

            if o.limit_price:
                trading_price = o.limit_price

            else:
                trading_price = op

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)

            if o.is_long:
                if 1 > o.units > 0:
                    size = int((self.execute.equity * o.units) / trading_price)
                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 - o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 + o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                if not o.is_parents:
                    add_position_long_order.append(o)

            elif o.is_short:

                if -1 < o.units < 0:
                    size = int((self.execute.equity * o.units) / trading_price)

                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 + o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 - o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                if not o.is_parents:
                    add_position_short_order.append(o)

            order_execute.append(o)
            self.work(ohlc, date=date, commission=commission)

        order_queue.clear()

        self.check_if_sl_or_sp(ohlc=ohlc, date=date, commission=commission)

    def check_if_sl_or_sp(self, ohlc, date, commission):
        for t in order_execute:
            origin_o = deepcopy(t).is_parents
            if util.touch_stop_loss(order=t, price=ohlc[3], date=date):

                t.replace(_unit=-t.units, _trading_price=t.stop_loss_prices, trading_date=date, _is_fill=False,
                          _is_parent=False, stop_loss=None)

            elif util.touch_stop_profit(order=t, price=ohlc[3], date=date):
                t.replace(_unit=-t.units, _trading_price=t.stop_profit_prices, trading_date=date, _is_fill=False,
                          _is_parent=False, stop_loss=None)

            if not origin_o:
                order_execute.remove(t)

        self.work(ohlc, date=date, commission=commission)

    def work(self, price, date, commission):

        self.execute.trading(price, date, commission)

    def liquidation(self, pos, price, date, commission):
        """
        clean the last position
        """
        o = Order(-1 * pos, limit_price=None, stop_loss=None, stop_profit=None, is_fill=False)
        setattr(o, 'trading_price', price[0])
        setattr(o, 'trading_date', date)
        order_execute.append(o)

        self.work(price=price, date=date, commission=commission)

    def get_log(self):
        log_dict = {'BuyDate': buy_date, 'BuyPrice': buy_price, 'BuyUnits': buy_unit, 'CashPaying': amnt_paying,
                    'SellDate': sell_date, 'SellPrice': sell_price, 'SellUnits': sell_unit,
                    'CashReceiving': amnt_receiving}

        log = pd.DataFrame(log_dict)

        for i in list(log_dict.values()):
            i.clear()

        return log


class Execute:
    def __init__(self, equity):
        self.__equity = equity

    def trading(self, price, date, commission):

        c = price[3]

        for t in order_execute:
            if not t.is_filled:
                position_list.append(t.units)

                if t.is_short and add_position_long_order and t.is_parents:
                    self.split_add_pos_order(t, add_position_long_order, commission)
                elif t.is_long and add_position_short_order and t.is_parents:
                    self.split_add_pos_order(t, add_position_short_order, commission)

                else:
                    self.fill(t, commission)

            if position() == 0 and t in order_execute: del order_execute[: order_execute.index(t) + 1]

    def fill(self, t, commission):
        adj_price = util.adjust_price(trade=t, commission=commission)

        if t.is_long:
            assert self.__equity >= adj_price * t.units, 'Your money is empty'

            buy_price.append(t.trading_price)
            buy_date.append(t.trading_date)
            buy_unit.append(t.units)
            amnt_paying.append(adj_price * t.units)

            self.__equity -= t.units * adj_price
            setattr(t, 'is_filled', True)

        elif t.is_short:

            sell_price.append(t.trading_price)
            sell_date.append(t.trading_date)
            sell_unit.append(t.units)
            amnt_receiving.append(abs(t.units) * adj_price)

            self.__equity += abs(t.units) * adj_price
            setattr(t, 'is_filled', True)

    def split_add_pos_order(self, trade_order, add_position_order: list, commission):
        """
        split the order which include overweight order into a list of single order and fill them
        e.g. a sell order [with 6 units has an parent order and an overweight order] becomes
        [an parent order with -4 units , an order with -2 units]
        """
        temp_order_list = []
        origin_trader_order_sign = np.sign(trade_order.units)
        if trade_order.is_short:
            parents_unit = trade_order.units + sum(abs(_o.units) for _o in add_position_order)
        else:
            parents_unit = trade_order.units - sum(abs(_o.units) for _o in add_position_order)
        trade_order.units = parents_unit
        if trade_order.units != 0:
            temp_order_list.append(trade_order)
        for _t in add_position_order:
            if np.sign(_t.units) == origin_trader_order_sign:
                temp_order_list.append(_t)

            else:
                ct = deepcopy(_t)

                ct.units = -_t.units
                ct.trading_date = trade_order.trading_date
                ct.trading_prices = trade_order.trading_price

                temp_order_list.append(ct)
        for temp_o in temp_order_list:
            self.fill(temp_o, commission)

        add_position_order.clear()

    @property
    def equity(self):
        return self.__equity


def position():
    return sum(size for size in position_list)
