from typing import List, Optional


from alphabt.order.order import Order
from alphabt.position.manager import PositionManager

class OrderManager:

    _order_queue = []

    @classmethod
    def add_order(cls, order: Order) -> None:

        reorganize_order_list = cls().reorganize_order()

        if reorganize_order_list is not None:
            # print(len(reorganize_order_list))

            cls._order_queue.extend(reorganize_order_list)
        else:

            cls._order_queue.append(order)


    def reorganize_order(self) -> Optional[List[Order]]:
        
        order_in_position = PositionManager._order_in_position
        the_newest_order = order_in_position[-1]
        the_newest_order_action = the_newest_order.action


        if the_newest_order_action == 'close' :

            ticker = the_newest_order.ticker
            close_price = the_newest_order.exit_price
            close_date = the_newest_order.exit_date



            # beause of the action of close position, 
            # the unit must mutiply -1 to origin order unit
            reorganize_unit = [-o.unit for o in order_in_position[: -1]]
            reorganize_order = [Order(ticker=ticker,
                                      unit=u,
                                      action='close',
                                      exit_date=close_date,
                                      exit_price = close_price) 
                                for u in reorganize_unit] 
                                
            return reorganize_order
        return None
    







