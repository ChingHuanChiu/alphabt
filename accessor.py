from typing import List


class Accessor:
    _buy_price: List = None
    _buy_date: List = None
    _buy_unit: List = None
    _sell_price: List = None
    _sell_date: List = None
    _sell_unit: List = None
    _order_queue: List = None
    _order_execute: List = None
    _add_position_long_order: List = None
    _add_position_short_order: List = None
    _amnt_paying: List = None
    _amnt_receiving: List = None
    _position_list: List = None

    @classmethod
    def initial(cls):
        cls._buy_price: List = []
        cls._buy_date: List = []
        cls._buy_unit: List = []
        cls._sell_price: List = []
        cls._sell_date: List = []
        cls._sell_unit: List = []
        cls._order_queue: List = []
        cls._order_execute: List = []
        cls._add_position_long_order: List = []
        cls._add_position_short_order: List = []
        cls._amnt_paying: List = []
        cls._amnt_receiving: List = []
        cls._position_list: List = [0]




class Position():
    """TODO: the final type is to be like -> Position['ticker'] = [position1, ...]
    
    """

    def __init__(self) -> None:
        pass
    
    # @staticmethod
    # def add(unit):
    #     Accessor._position_list.append(unit)

    @staticmethod
    def status() -> int:
        return sum(size for size in Accessor._position_list)




