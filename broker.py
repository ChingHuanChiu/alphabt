from typing import Union, List
from functools import partial


from alphabt.accessor import Accessor
from alphabt.order import Order
from copy import deepcopy
import pandas as pd
import numpy as np
from alphabt import util


class Broker:
    def __init__(self, equity:float) -> None:

        self.execute: Execute = Execute(equity)
        self.accessor: Accessor = Accessor()  

    def make_order(self, unit: Union[float, int], limit_price: float, 
                stop_loss: float, stop_profit: float) -> None:

        self.accessor._order_queue.append(Order(unit, limit_price, stop_loss, stop_profit))


    def check_order(self, ohlc: np.array, date: pd.Timestamp, commission: Union[None, float]) -> None:
        """check the order and set the information to order by different condition
        """

        op = ohlc[0]

        for o in self.accessor._order_queue:
            if position() != 0 and position() + o.units != 0 and len(self.accessor._order_queue) == 1:
                o.is_parents = False

            if o.limit_price:
                trading_price = o.limit_price

            else:
                trading_price = op

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)

            if o.is_long:
                if 1 > o.units > 0 :
                    o.units = 1 if o.units == 0.0001 else o.units
                    size = int((self.execute.equity * o.units) / trading_price)
                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 - o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 + o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                if not o.is_parents:
                    self.accessor._add_position_long_order.append(o)

            elif o.is_short:

                if -1 < o.units < 0:
                    o.units = -1 if o.units == -0.0001 else o.units
                    size = int((self.execute.equity * o.units) / trading_price)

                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 + o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 - o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                if not o.is_parents:
                    self.accessor._add_position_short_order.append(o)

            self.accessor._order_execute.append(o)
            self._work(commission=commission)

        self.accessor._order_queue.clear()

        self.check_if_sl_or_sp(ohlc=ohlc, date=date, commission=commission)


    def check_if_sl_or_sp(self, ohlc: np.array, date: pd.Timestamp, commission: Union[None, float]) -> None:
        
        for t in self.accessor._order_execute:

            partial_method = partial(t.replace, _unit=-t.units, trading_date=date, _is_fill=False,
                          _is_parent=False, stop_loss=None)

            parent_order = deepcopy(t).is_parents

            if util.touch_stop_loss(order=t, price=ohlc[3], date=date):

                partial_method(_trading_price=t.stop_loss_prices)

            elif util.touch_stop_profit(order=t, price=ohlc[3], date=date):

                partial_method(_trading_price=t.stop_profit_prices)

            # _order_execute only with the parent orders
            if not parent_order:
                self.accessor._order_execute.remove(t)

        self._work(commission=commission)


    def _work(self, commission):

        self.execute.trading(commission)


    def liquidation(self, pos, price, date, commission):
        """clean the last position
        """
        o = Order(-1 * pos, limit_price=None, stop_loss=None, stop_profit=None, is_fill=False)
        setattr(o, 'trading_price', price[0])
        setattr(o, 'trading_date', date)
        self.accessor._order_execute.append(o)

        self._work(commission=commission)


    def get_log(self):

        log_dict = {'BuyDate': self.accessor._buy_date, 'BuyPrice': self.accessor._buy_price, 'BuyUnits': self.accessor._buy_unit, 'CashPaying': self.accessor._amnt_paying,
                    'SellDate': self.accessor._sell_date, 'SellPrice': self.accessor._sell_price, 'SellUnits': self.accessor._sell_unit,
                    'CashReceiving': self.accessor._amnt_receiving}

        log = pd.DataFrame(log_dict)

        for i in list(log_dict.values()):
            i.clear()

        return log


class Execute:
    def __init__(self, equity:float):
        self._equity = equity
        self.accessor: Accessor = Accessor() 

    def trading(self, commission: Union[None, float]):

        for t in self.accessor._order_execute:

            if not t.is_filled:
                self.accessor._position_list.append(t.units)

                if t.is_short and self.accessor._add_position_long_order and t.is_parents:
                    self.split_add_pos_order(t, self.accessor._add_position_long_order, commission)

                elif t.is_long and self.accessor._add_position_short_order and t.is_parents:
                    self.split_add_pos_order(t, self.accessor._add_position_short_order, commission)

                else:
                    self.fill(t, commission)

            if position() == 0 and t in self.accessor._order_execute: del self.accessor._order_execute[: self.accessor._order_execute.index(t) + 1]


    def fill(self, t: Order, commission: Union[None, float]):
        adj_price = util.adjust_price(trade=t, commission=commission)

        if t.is_long:
            assert self._equity >= adj_price * t.units, 'Your money is empty'

            self.accessor._buy_price.append(t.trading_price)
            self.accessor._buy_date.append(t.trading_date)
            self.accessor._buy_unit.append(t.units)
            self.accessor._amnt_paying.append(adj_price * t.units)

            self._equity -= t.units * adj_price
            setattr(t, 'is_filled', True)

        elif t.is_short:

            self.accessor._sell_price.append(t.trading_price)
            self.accessor._sell_date.append(t.trading_date)
            self.accessor._sell_unit.append(t.units)
            self.accessor._amnt_receiving.append(abs(t.units) * adj_price)

            self._equity += abs(t.units) * adj_price
            setattr(t, 'is_filled', True)

    def split_add_pos_order(self, trade_order: Order, add_position_order: List[Order], commission: Union[None, float]):
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
        return self._equity

def position():
    return sum(size for size in Accessor()._position_list)
