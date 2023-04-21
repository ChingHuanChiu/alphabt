
from typing import Union, List, Optional

import pandas as pd

from alphabt.order.order import Order
from alphabt.order.manager import OrderManager
from alphabt.position.manager import PositionManager
from alphabt.equity.manager import EquityManager
from alphabt.broker.condition import StopLossCondition, StopProfitCondition


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


    def review_order(self, current_price, date: pd.Timestamp) -> None:
        """review the orders which are in order_in_position queue, the following jobs:
        1. check the order if touch the stop_loss and stop_profit condiction
           every single row data
        2. if the action of order is 'close' then clean the order_in_position queue
           from PositionManager

        """
        the_last_order = PositionManager._order_in_position[-1]
        in_position_orders = PositionManager._order_in_position[: -1]

        if (the_last_order.action == 'close' and 
            PositionManager.status == 0):

            PositionManager.clear()
        
        else:
        
            for in_position_order in in_position_orders:
                
                if (StopLossCondition.match(trigger_price=in_position_order.stop_loss_price,
                                            current_price=current_price,
                                            direction=in_position_order.action) or

                    StopProfitCondition.match(trigger_price=in_position_order.stop_profit_price,
                                              current_price=current_price,
                                              direction=in_position_order.action)):
                    
                    self.make_order(unit=-1*in_position_order.unit,
                                    stop_loss=None, 
                                    stop_profit=None,
                                    action='close',
                                    ticker=in_position_order.ticker,
                                    trading_price=current_price,
                                    trading_date=date)
                

    def liquidate_position(self, price: float, date: str) -> None:

        current_position = PositionManager.status
        ticker = PositionManager._order_in_position[-1].ticker

        self.make_order(unit=-1*current_position,
                        stop_loss=None, 
                        stop_profit=None,
                        action='close',
                        ticker=ticker,
                        trading_price=price,
                        trading_date=date)
  



    