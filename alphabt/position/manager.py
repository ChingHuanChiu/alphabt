import numpy as np

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
    def close(cls) -> None:
        idx_close_order = cls.find_close_order_index()

        cls._order_in_position = cls._order_in_position[idx_close_order + 1:]



    @classmethod
    def find_close_order_index(cls) -> int:
        """find the last close order
        """

        in_position_order_action_array = \
            np.array([o.action for o in cls._order_in_position])
        
        idx = np.where(in_position_order_action_array == 'close')[-1]

        length_close_idx = len(idx)
        if length_close_idx == 0:
            return 0
        return int(idx[0])



        
        
