from accessor import *
from order import Order
from copy import deepcopy, copy
import pandas as pd
import numpy as np


class Broker:
    def __init__(self, equity):

        self.execute = Execute(equity)  # Execute

    def make_order(self, unit, limit_price, stop_loss):

        order_queue.append(Order(unit, limit_price, stop_loss))

    def check_order(self, ohlc, date):
        """
        check the order and set the information of order by different condition
        """

        op = ohlc.open

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

                if not o.is_parents:
                    add_position_long_order.append(o)

            elif o.is_short:

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 + o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if not o.is_parents:
                    add_position_short_order.append(o)

            order_execute.append(o)
        order_queue.clear()

    def work(self, price, date):
        """
        price: Series with columns: Open, Close, High, Low
        """
        self.execute.trading(price, date)

    def liquidation(self, pos, price, date):
        """
        clean the last position
        """
        o = Order(-1 * pos, limit_price=None, stop_loss=None, is_fill=False)
        setattr(o, 'trading_price', price.open)
        setattr(o, 'trading_date', date)
        order_execute.append(o)

        self.work(price=price, date=date)


    def get_log(self):
        log_dict = {'BuyDate': buy_date, 'BuyPrice': buy_price, 'BuyUnits': buy_unit, 'SellDate': sell_date,
                    'SellPrice': sell_price, 'SellUnits': sell_unit}

        log = pd.DataFrame(log_dict)

        for i in list(log_dict.values()):
            i.clear()

        return log


class Execute:
    def __init__(self, equity):
        self.__equity = equity

    def trading(self, price, date):

        c = price.close

        for t in order_execute:
            if not t.is_filled:
                position_list.append(t.units)

                if t.is_short and add_position_long_order and t.is_parents:
                    # print(t.trading_date)
                    self.split_add_pos_order(t, add_position_long_order)
                elif t.is_long and add_position_short_order and t.is_parents:
                    self.split_add_pos_order(t, add_position_short_order)

                else:
                    self.fill(t)

            if self._touch_stop_loss(order=t, price=c):
                origin_o = deepcopy(t).is_parents
                t.replace(-t.units, t.stop_loss_price, date, False, is_parent=False)
                if not origin_o:
                    order_execute.remove(t)

            if position() == 0 and t in order_execute: del order_execute[: order_execute.index(t) + 1]

    def fill(self, t):

        if t.is_long:

            assert self.__equity >= t.trading_price * t.units

            buy_price.append(t.trading_price)
            buy_date.append(t.trading_date)
            buy_unit.append(t.units)

            self.__equity -= t.units * t.trading_price
            setattr(t, 'is_fill', True)

        elif t.is_short:

            sell_price.append(t.trading_price)
            sell_date.append(t.trading_date)
            sell_unit.append(t.units)
            self.__equity += abs(t.units) * t.trading_price
            setattr(t, 'is_fill', True)

    @staticmethod
    def _touch_stop_loss(order, price):

        if order.is_long:
            con = order.stop_loss and price <= order.stop_loss_price and order.is_filled and order.trading_date not in [
                order.trading_date for order in order_execute]

            return con
        else:
            con = order.stop_loss and price <= order.stop_loss_price and order.is_filled and order.trading_date not in [
                order.trading_date for order in order_execute]

            return con

    def split_add_pos_order(self, trade_order, add_position_order: list):
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
                ct.trading_prices = trade_order.trading_prices

                temp_order_list.append(ct)
        for temp_o in temp_order_list:

            self.fill(temp_o)

        add_position_order.clear()

    @property
    def equity(self):
        return self.__equity

#
# def position(size):
#     """
#     TODO : become class
#     """
#     try:
#         position.pos += size
#
#     except:
#         position.pos = size
#     return position.pos

def position():
    return sum(size for size in position_list)
