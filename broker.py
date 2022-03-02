import sys

from matplotlib import units
sys.path.extend(['./'])
from typing import Union, List
from functools import partial


from copy import deepcopy
import pandas as pd
import numpy as np

from alphabt.accessor import Accessor, Position
from alphabt.order import Order
from alphabt import util


class Broker:

    def __init__(self, equity, commission: Union[None, float]) -> None:
        self.commission = commission
        self.equity_instance = equity
        self.execute: Execute = Execute(self.equity_instance, self.commission)

    @staticmethod
    def make_order(unit: Union[float, int], stop_loss: float, stop_profit: float) -> None:

        Accessor._order_queue.append(Order(unit, stop_loss, stop_profit))


    def check_order(self, ohlc: np.array, date: pd.Timestamp) -> None:
        """check the order and set the information to order by different condition
        """

        open_price = ohlc[0]

        for o in Accessor._order_queue:

            position = Position.status()

            if position != 0 and position + o.units != 0 and len(Accessor._order_queue) == 1:
                o.is_parents = False

           
            trading_price = open_price

            setattr(o, 'trading_price', trading_price)
            setattr(o, 'trading_date', date)

            if o.is_long:

                if 1 > o.units > 0 :
                    o.units = 1 if o.units == 0.0001 else o.units
                    
                    size = int((self.equity_instance.equity * o.units) / util.adjust_price(trade=o, commission=self.commission))
                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 - o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 + o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                if not o.is_parents:
                    Accessor._add_position_long_order.append(o)

            elif o.is_short:

                if -1 < o.units < 0:
                    o.units = -1 if o.units == -0.0001 else o.units
                    size = int((self.equity_instance.equity * o.units) / util.adjust_price(trade=o, commission=self.commission))

                    setattr(o, 'units', size)

                if o.stop_loss:
                    stop_loss_price = o.trading_price * (1 + o.stop_loss)
                    setattr(o, 'stop_loss_prices', stop_loss_price)

                if o.stop_profit:
                    stop_profit_price = o.trading_price * (1 - o.stop_profit)
                    setattr(o, 'stop_profit_prices', stop_profit_price)

                # if the order is to increase position
                if not o.is_parents:
                    Accessor._add_position_short_order.append(o)

            Accessor._order_execute.append(o)
            self._work()

        Accessor._order_queue.clear()
        self.check_if_sl_or_sp(ohlc=ohlc, date=date)



    def check_if_sl_or_sp(self, ohlc: np.array, date: pd.Timestamp) -> None:
        
        for t in Accessor._order_execute:

            partial_method = partial(t.replace, _unit=-t.units, trading_date=date, _is_fill=False,
                          _is_parent=False, stop_loss=None)

            parent_order = deepcopy(t).is_parents

            if util.touch_stop_loss(order=t, price=ohlc[3], date=date):

                partial_method(_trading_price=t.stop_loss_prices)

            elif util.touch_stop_profit(order=t, price=ohlc[3], date=date):

                partial_method(_trading_price=t.stop_profit_prices)

            # _order_execute only with the parent orders
            if not parent_order:
                Accessor._order_execute.remove(t)

        self._work()


    def _work(self) -> None:

        self.execute.trading()


    def liquidation(self, pos, price, date) -> None:
        """clean the  position
        """
        o = Order(-1 * pos, stop_loss=None, stop_profit=None, is_fill=False)
        setattr(o, 'trading_price', price[0])
        setattr(o, 'trading_date', date)
        Accessor._order_execute.append(o)

        self._work()


    def get_log(self) -> pd.DataFrame:

        log_dict = {'BuyDate': Accessor._buy_date, 'BuyPrice': Accessor._buy_price, 'BuyUnits': Accessor._buy_unit, 'CashPaying': Accessor._amnt_paying,
                    'SellDate': Accessor._sell_date, 'SellPrice': Accessor._sell_price, 'SellUnits': Accessor._sell_unit,
                    'CashReceiving': Accessor._amnt_receiving}

        log = pd.DataFrame(log_dict)

        return log


class Execute:

    def __init__(self, equity, commission: Union[None, float]):
        
        self.equity_instance = equity
        self.commission = commission


    def trading(self):

        for t in Accessor._order_execute:
            if not t.is_filled:
                Accessor._position_list.append(t.units)

                if t.is_short and Accessor._add_position_long_order and t.is_parents:
                    self.split_add_pos_order(t, Accessor._add_position_long_order)


                elif t.is_long and Accessor._add_position_short_order and t.is_parents:
                    self.split_add_pos_order(t, Accessor._add_position_short_order)


                else:

                    self.fill(t)

            if Position.status() == 0 and t in Accessor._order_execute: del Accessor._order_execute[: Accessor._order_execute.index(t) + 1]


    def fill(self, t: Order):

        adj_price = util.adjust_price(trade=t, commission=self.commission)

        if t.is_long:
            assert self.equity_instance.equity >= adj_price * t.units, 'Your money is not enough'

            Accessor._buy_price.append(t.trading_price)
            Accessor._buy_date.append(t.trading_date)
            Accessor._buy_unit.append(t.units)
            Accessor._amnt_paying.append(adj_price  * t.units)

            self.equity_instance.equity -= t.units * adj_price 
            setattr(t, 'is_filled', True)

        elif t.is_short:

            Accessor._sell_price.append(t.trading_price)
            Accessor._sell_date.append(t.trading_date)
            Accessor._sell_unit.append(t.units)
            Accessor._amnt_receiving.append(abs(t.units) * adj_price )
            self.equity_instance.equity += abs(t.units) * adj_price 
            setattr(t, 'is_filled', True)


    def split_add_pos_order(self, trade_order: Order, add_position_order: List[Order]):
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

                _t.units = -_t.units
                _t.trading_date = trade_order.trading_date
                _t.trading_price = trade_order.trading_price

                temp_order_list.append(_t)
        for temp_o in temp_order_list:
            self.fill(temp_o)

        add_position_order.clear()





