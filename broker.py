from accessor import *
from order import Order
from copy import deepcopy
import pandas as pd


class Broker:
    def __init__(self, equity):

        self.execute = Execute(equity)  # Execute

    def make_order(self, unit, limit_price, stop_loss):

        order_queue.append(Order(unit, limit_price, stop_loss))

    def check_order(self, ohlc, date):
        """
        check the order and set the information of order by different condition
        TODO think the another way to avoid too many "if"
        """

        op = ohlc.open

        for o in order_queue:

            # check the order type, if market order, trading price is next open
            if o.limit_price:
                trading_price = o.limit_price

            else:
                trading_price = op

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)
            # print(o.trading_date)

            if o.is_long:
                if 1 > o.units > 0:
                    size = int((self.execute.equity * o.units) / trading_price)
                    setattr(o, 'units', size)

                if position_list[-1] < -1:
                    setattr(o, 'units', -position_list[-1])

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 - o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if not o.is_parents:
                    print('a', 'pos is', position_list[-1], 'date', o.trading_date)
                    add_position_long_order.append(o)

            elif o.is_short:
                if position_list[-1] > 1:
                    setattr(o, 'units', -position_list[-1])

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 + o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if not o.is_parents:
                    print('a2', position_list[-1])
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
                position_list.append(position(t.units))

                if t.is_short and add_position_long_order:
                    self.split_add_pos_order(t, add_position_long_order)

                elif t.is_long and add_position_short_order:
                    self.split_add_pos_order(t, add_position_short_order)

                else:
                    self.fill(t)

            if self._touch_stop_loss(order=t, price=c):
                if t.is_long and not t.is_parents:
                    add_position_long_order.remove(t)
                elif t.is_short and not t.is_parents:

                    add_position_short_order.remove(t)
                t.replace(-t.units, t.stop_loss_price, date, False)

    def fill(self, t):

        if t.is_long:

            assert self.__equity >= t.trading_price * t.units

            # print(t.trading_price)

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

        if position_list[-1] == 0: del order_execute[: order_execute.index(t) + 1]

    def _touch_stop_loss(self, order, price):
        # print(order.trading_date, order.stop_loss and price <= order.stop_loss_price and order.is_filled)
        if order.is_long:

            return order.stop_loss and price <= order.stop_loss_price and order.is_filled
        else:
            return order.stop_loss and price >= order.stop_loss_price and order.is_filled

    def split_add_pos_order(self, trade_order, add_position_order: list):
        parents_unit = trade_order.units + sum(_o.units for _o in add_position_order)
        trade_order.units = parents_unit
        self.fill(trade_order)
        for _t in add_position_long_order:
            ct = deepcopy(_t)

            ct.units = -_t.units
            ct.trading_date = trade_order.trading_date
            ct.trading_prices = trade_order.trading_prices
            self.fill(ct)
        add_position_order.clear()

    @property
    def equity(self):
        return self.__equity


def position(size):
    """
    TODO : become class
    """
    try:
        position.pos += size

    except:
        position.pos = size
    return position.pos

