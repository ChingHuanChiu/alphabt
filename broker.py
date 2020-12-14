from collections import defaultdict
from accessor import *
from order import Order
import pandas as pd
import numpy as np


class Broker:
    def __init__(self, equity):

        self.execute = Execute(equity)  # Execute

    def make_order(self, unit, limit_price, stop_loss):
        order_queue.append(Order(unit, limit_price, stop_loss))

    def check_order(self, ohlc, date):
        # buy in open price
        op = ohlc.open
        # print('order_queue', order_queue, date)
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
                print('size', size)
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

            # if the order is not one to one(one buy order pair with one sell order, and vice versa),
            # change the order to match the FIFO process
            FIFO_order = []

            if order_execute and abs(o.units) != abs(order_execute[-1].units) and \
                    np.sign(o.units) != np.sign(order_execute[-1].units) and position_list[-1] != 0:
                print(o.units, order_execute[-1].units)
                print("FIFO Process")
                print(order_execute)
                for t in order_execute[::-1]:
                    if np.sign(t.units) != np.sign(o.units):
                        setattr(o, 'units', -t.units)
                        FIFO_order.insert(0, o)
                    else:
                        break

            if FIFO_order:
                order_execute.extend(FIFO_order)
            else:
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
        # print(len(buy_date), len(sell_date))
        log = pd.DataFrame(log_dict)

        for i in list(log_dict.values()):
            i.clear()

        return log


class Execute:
    def __init__(self, equity):
        self.__equity = equity

    def trading(self, price, date):
        h = price.high
        c = price.close
        for t in order_execute:

            if t.is_long and not t.is_filled:

                # print(self.equity, t.trading_price, t.units, t.trading_price * t.units)
                assert self.__equity >= t.trading_price * t.units

                # print(t.trading_price)

                buy_price.append(t.trading_price)
                buy_date.append(t.trading_date)
                buy_unit.append(t.units)
                position_list.append(position(t.units))
                self.__equity -= t.units * t.trading_price
                setattr(t, 'is_fill', True)

            elif t.is_short and not t.is_filled:

                sell_price.append(t.trading_price)
                sell_date.append(t.trading_date)
                sell_unit.append(t.units)
                position_list.append(position(t.units))
                self.__equity += t.units * t.trading_price
                setattr(t, 'is_fill', True)

            else:
                continue

            if t.is_long and t.stop_loss and c <= t.stop_loss_price and t.is_filled:
                print('in long')
                # print(price)
                t.replace(-t.units, t.stop_loss_price, date, False)

            elif t.is_short and t.stop_loss and c >= t.stop_loss_price and t.is_filled:
                print('in short')
                t.replace(t.units, t.stop_loss_price, date, False)

    @property
    def equity(self):
        return self.__equity


def position(size):
    try:
        position.pos += size

    except:
        position.pos = size
    return position.pos
