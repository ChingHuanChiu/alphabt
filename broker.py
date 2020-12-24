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
        # buy in open price
        op = ohlc.open
        for o in order_queue:

            # check the order type, if market order, trading price is next open
            if o.limit_price:
                trading_price = o.limit_price

            else:
                trading_price = op

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)

            if o.is_long and 1 > o.units > 0:
                size = int((self.execute.equity * o.units) / trading_price)

                setattr(o, 'units', size)
            elif o.is_short and position_list[-1] > 1:
                setattr(o, 'units', -position_list[-1])

            # check stop loss condition
            # stop loss is ratio
            # the assumption is that if touch the stop loss price we can trade with this price
            stop_loss_price = None
            if o.stop_loss and o.is_long:

                stop_loss_price = o.trading_price * (1 - o.stop_loss)

            elif o.stop_loss and o.is_short:
                stop_loss_price = o.trading_price * (1 + o.stop_loss)
            setattr(o, 'stop_loss_prices', stop_loss_price)

            if not o.is_parents and o.is_long:
                # print('in not parents in long', o.trading_date, o.units, order_execute[-1].trading_date)
                add_position_long_order.append(o)
            elif not o.is_parents and o.is_short:
                add_position_short_order.append(o)
            order_execute.append(o)
        order_queue.clear()
        # print('after order_queue', order_queue, date)

    def work(self, price, date):
        """
        price: Series with columns: Open, Close, High, Low
        """
        # print(type(price), price)
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

                    short_parents_unit = t.units + sum(_o.units for _o in add_position_long_order)
                    t.units = short_parents_unit
                    # print('after', t.units, t.trading_date)
                    self.fill(t)
                    for _t in add_position_long_order:
                        ct = deepcopy(_t)

                        ct.units = -_t.units
                        ct.trading_date = t.trading_date
                        ct.trading_prices = t.trading_prices
                        self.fill(ct)
                    add_position_long_order.clear()

                elif t.is_long and add_position_short_order:
                    parents_unit = t.units - sum(_o.units for _o in add_position_short_order)
                    t.units = parents_unit
                    self.fill(t)
                    for _t in add_position_short_order:
                        ct = deepcopy(_t)
                        ct.units = -_t.units
                        ct.trading_date = t.trading_date
                        ct.trading_prices = t.trading_prices
                        self.fill(ct)
                    add_position_short_order.clear()

                else:
                    self.fill(t)

            if self._touch_stop_loss(order=t, price=c):
                print('in sl')
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

        if position_list[-1] == 0: order_execute.clear()

    def _touch_stop_loss(self, order, price):

        if order.is_long:

            return order.stop_loss and price <= order.stop_loss_price and order.is_filled
        else:
            return order.stop_loss and price >= order.stop_loss_price and order.is_filled



    @property
    def equity(self):
        return self.__equity


def position(size):
    """
    TO DO : become class
    """
    try:
        position.pos += size

    except:
        position.pos = size
    return position.pos

