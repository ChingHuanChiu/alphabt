from typing import List, Optional


from alphabt.order.order import Order
from alphabt.position.manager import PositionManager

class OrderManager:

    _order_queue = []

    @classmethod
    def add_order(cls, 
                  order: Order, 
                  send_to_queue_when_overweight: bool) -> None:



        reorganize_order_list = cls().reorganize_order()

        if reorganize_order_list is not None:
            if not send_to_queue_when_overweight:
                return None
            cls._order_queue.extend(reorganize_order_list)
        else:

            cls._order_queue.append(order)


    def reorganize_order(self) -> Optional[List[Order]]:
        
        order_in_position = PositionManager._order_in_position
        close_order_idx = PositionManager.find_close_order_index()

        if close_order_idx == 0:
            return None

        close_order = order_in_position[close_order_idx]


        if abs(close_order.unit) >= 2:

            ticker = close_order.ticker
            close_price = close_order.exit_price
            close_date = close_order.exit_date

            # beause of the action of close position, 
            # the unit must mutiply -1 to origin order unit
            reorganize_unit = [-o.unit for o in order_in_position[: close_order_idx]]
            reorganize_order = [Order(ticker=ticker,
                                      unit=u,
                                      action='close',
                                      exit_date=close_date,
                                      exit_price = close_price) 
                                for u in reorganize_unit] 
            return reorganize_order + order_in_position[close_order_idx + 1: ]
        return None
    





