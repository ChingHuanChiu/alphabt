from collections import defaultdict
from accessor import *
from order import Order
import pandas as pd


class Broker:
    def __init__(self, equity):
        self.equity = equity

        self.execute = Execute(self.equity) # Execute
        # order_queue = [] # Because the list must be clear per signal, the list is not in accessor
        # self.order_execute = []

    def make_order(self, unit, limit_price, stop_loss):
        order_queue.append(Order(unit, limit_price, stop_loss))

    def check_order(self, ohlc, date):
        op = ohlc.open
        print('order_queue', order_queue, date)
        for o in order_queue:

            if o.limit_price:
                trading_price = o.limit_price

            else:
                trading_price = op  # if market order, trading price is next open

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)

            # check stop loss condition
            # stop loss is ratio
            # the assumption is if touch the stop loss price we can trade with this price
            stop_loss_price = None
            if o.stop_loss and o.is_long:
                stop_loss_price = o.trading_price * (1 - o.stop_loss)

            elif o.stop_loss and o.is_short:

                stop_loss_price = o.trading_price * (1 + o.stop_loss)
            setattr(o, 'stop_loss_price', stop_loss_price)

            order_execute.append(o)
        order_queue.clear()
        print('after order_queue', order_queue, date)

    def work(self, price):
        """
        price: Series with columns: Open, Close, High, Low
        """
        self.execute.trading(price)

    def get_log(self):
        print(pd.Series(buy_date))
        print(pd.Series(buy_price))
        print(pd.Series(buy_unit))
        print(pd.Series(sell_price))
        print(pd.Series(sell_date))
        print(pd.Series(sell_unit))
        log = pd.DataFrame({'BuyDate': buy_date, 'BuyPrice': buy_price, 'BuyUnits': buy_unit, 'SellDate': sell_date,
                            'SellPrice': sell_price, 'SellUnits': sell_unit})
        return log


class Execute:
    def __init__(self, equity):
        self.equity = equity
        # self.position = 0
        # self.log_dict = defaultdict(list)

    def trading(self, price):
        h = price.high
        c = price.close
        for t in order_execute:
            if t.is_long:
                assert self.equity >= t.trading_price * t.units
                print(t.trading_price)
                buy_price.append(t.trading_price)
                buy_date.append(t.trading_date)
                buy_unit.append(t.units)
                position_list.append(position(t.units))
                self.equity -= t.units * t.trading_price
                del order_execute[0]

                if t.stop_loss and h <= t.stop_loss_price:
                    replace_order = t.replace(t.units, t.stop_loss_price)
                    order_execute.insert(0, replace_order)

            elif t.is_short:
                sell_price.append(t.trading_price)
                sell_date.append(t.trading_date)
                sell_unit.append(t.units)

                position_list.append(position(t.units))
                self.equity += t.units * t.trading_price
                del order_execute[0]

                if t.stop_loss and c >= t.stop_loss_price:
                    replace_order = t.replace(t.units, t.stop_loss_price)
                    order_execute.insert(0, replace_order)

            else:
                continue


def position(size):
    try:
        position.pos += size

    except:
        position.pos = size
    return position.pos