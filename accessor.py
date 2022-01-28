from typing import List

class Accessor:
    _buy_price: List = []
    _buy_date: List = []
    _buy_unit: List = []
    _sell_price: List = []
    _sell_date: List = []
    _sell_unit: List = []
    _order_queue: List = []
    _order_execute: List = []
    _add_position_long_order: List = []
    _add_position_short_order: List = []
    _amnt_paying: List = []
    _amnt_receiving: List = []
    _position_list: List = [0]