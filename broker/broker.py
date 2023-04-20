
from typing import Union, List, Optional
from functools import partial


from copy import deepcopy
import pandas as pd
import numpy as np

from alphabt.accessor import Accessor, Position
from alphabt.order import Order
from alphabt import util


from alphabt.order.order import Order
from alphabt.order.manager import OrderManager
from alphabt.position.manager import PositionManager
from alphabt.equity.manager import EquityManager


class Broker:

    def __init__(self, 
                 equity_manager: EquityManager, 
                 position_manager: PositionManager,
                 order_manager: OrderManager
                 ) -> None:
        # self.commission = commission
        self.equity_manager = equity_manager
        self.position_manager = position_manager
        self.order_manager = order_manager


    @staticmethod
    def make_order(unit: Union[float, int], 
                   stop_loss: Optional[float], 
                   stop_profit: Optional[float],
                   action: str,
                   ticker: str,
                   trading_price: float,
                   trading_date: str
                   ) -> None:
        
        entry_date = trading_date
        exit_date = None
        # TODO: need to consider commission
        entry_price = trading_price
        exit_price = None

        if action == 'long':
            stop_loss_price = trading_price * (1-stop_loss) if stop_loss is not None else None
            stop_profit_price = trading_price * (1 + stop_profit) if stop_profit is not None else None

        elif action == 'short':
            stop_loss_price = trading_price * (1+stop_loss) if stop_loss is not None else None
            stop_profit_price = trading_price * (1-stop_profit) if stop_profit is not None else None

        else:
            entry_date = None
            exit_date = trading_date
            entry_price = None
            exit_price = trading_price

        order_info = {
                      "ticker": ticker,
                      "unit": unit,
                      "action": action,
                      "stop_loss_price": stop_loss_price,
                      "stop_profit_price": stop_profit_price,
                      "entry_date": entry_date,
                      "exit_date": exit_date,
                      "entry_price": entry_price,
                      "exit_price": exit_price
                     }
        order = Order(**order_info)
        PositionManager.add_position_from_order(order)
        OrderManager.add_order(order)


    def review_order(self, ohlc: np.array, date: pd.Timestamp) -> None:
        """review the orders which are in order_in_position queue, the following jobs:
        1. check the order if touch the stop_loss and stop_profit condiction
           every signle row data
        2. if the action of order is 'close' then clean the order_in_position queue
           from PositionManager

        """
        the_last_order = PositionManager._order_in_position[-1]

        if the_last_order.action == 'close':
            PositionManager.clear()
        
        else:
            pass


    def touch_stop_loss(self, 
                        stop_loss_price: float, 
                        current_price: float,
                        direction: str
                        ) -> bool:
        """the current price is set to 'close' price
        TODO: confirm that using close price as current price is appropriate or not  
        
        """
        if direction == 'long':
            return current_price <= stop_loss_price
        else:
            return  current_price >= stop_loss_price



      





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





