from collections import defaultdict
from typing import Union, List, Optional, Dict, Any

import pandas as pd

from alphabt.order.order import Order
from alphabt.broker.condition import StopLossCondition, StopProfitCondition


class Broker:
    
    equity_manager = None
    position_manager = None
    order_manager = None


    @classmethod
    def make_order(cls,
                   unit: Union[float, int], 
                   stop_loss: Optional[float], 
                   stop_profit: Optional[float],
                   action: str,
                   ticker: str,
                   trading_price: float,
                   trading_date: pd.Timestamp
                   ) -> None:
        
        entry_date = trading_date
        exit_date = None
        entry_price = trading_price
        exit_price = None
        stop_loss_price = None
        stop_profit_price = None

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

        cls.position_manager.add_position_from_order(order)

        cls.order_manager.add_order(order)
        
        trading_turnover_value = trading_price * unit
        cls.equity_manager.deal_with_cost_from_order(order, 
                                                     abs(trading_turnover_value))

        cls.equity_manager.equity += trading_turnover_value
        trading_cost = order.commission_cost + order.tax_cost
        cls.equity_manager.equity -= trading_cost
        cls.equity_manager.add_to_queue()


    def review_order(self, current_price, date: pd.Timestamp) -> None:
        """review the orders which are in order_in_position queue, the following jobs:
        1. check the order if touch the stop_loss and stop_profit condiction
           every single row data
        2. if the action of order is 'close' then clean the order_in_position queue
           from PositionManager

        """
        if not self.position_manager._order_in_position:
            return None

        the_last_order = self.position_manager._order_in_position[-1]
        in_position_orders = self.position_manager._order_in_position[: -1]

        if (the_last_order.action == 'close' and 
            self.position_manager.status() == 0):
            self.position_manager.clear()
        
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


    def get_result_with_processing_order(self) -> Dict[str, List[Any]]:

        result = defaultdict(list)
        for order in self.order_manager._order_queue:

            result['Ticket'].append(order.ticker)
            result['unit'].append(order.unit)
            result['action'].append(order.action)
            result['EntryDate'].append(order.entry_date)
            result['EntryPrice'].append(order.entry_price)
            result['ExitDate'].append(order.exit_date)
            result['ExitPrice'].append(order.exit_price)
            result['Commission'].append(order.commission_cost)
            result['Tax'].append(order.tax_cost)

        return result


    def liquidate_position(self, price: float, date: pd.Timestamp) -> None:

        current_position = self.position_manager.status()
        ticker = self.position_manager._order_in_position[-1].ticker

        self.make_order(unit=-1*current_position,
                        stop_loss=None, 
                        stop_profit=None,
                        action='close',
                        ticker=ticker,
                        trading_price=price,
                        trading_date=date)
  



    