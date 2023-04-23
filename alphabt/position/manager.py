

class PositionManager:

    _order_in_position = []


    @classmethod
    def status(cls) -> int:
        """the current status of position 
        """
        return sum(order.unit  for order in cls._order_in_position)


    @classmethod
    def add_position_from_order(cls, order) -> None:
        """add new position order to position list
        """
        cls._order_in_position.append(order)


    @classmethod
    def clear(cls) -> None:

        cls._order_in_position.clear()
