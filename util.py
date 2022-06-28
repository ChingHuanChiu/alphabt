from typing import Union

import pandas as pd

from alphabt.accessor import Accessor
from alphabt.order import Order 


def reset_data(data_frame: pd.DataFrame) -> pd.DataFrame:
    data_frame.index = pd.to_datetime(data_frame.index)
    data_frame.columns = [c.lower() for c in data_frame.columns]
    if 'symbol' in data_frame.columns:
        data_frame = data_frame.rename(columns={'symbol': 'ticker'})
    data_frame = data_frame[['open', 'high', 'low', 'close', 'volume', 'ticker']]
    return data_frame


def adjust_price(trade: Order, commission: Union[None, float]) -> float:
    price = trade.trading_price
    if commission is not None:
        assert 0 < commission < 1, 'commision must in (0, 1)'

        if trade.is_long:
            adj_price = price * (1 + commission)
        else:
            adj_price = price * (1 - commission)
        return adj_price
    else:
        return price


def print_result(sharpe, calmar) -> None:
    print('-----------------------------|')
    print('sharpe ratio', '|', sharpe, '--------|')
    print('-----------------------------|')
    print('calmar ratio', '|', calmar, '--------|')
    print('-----------------------------|')



accessor = Accessor
def touch_stop_loss(order: Order, price: float, date:pd.Timestamp) -> bool:

    if order.is_long:
        con = order.stop_loss and price <= order.stop_loss_prices and order.is_filled and date not in [
            order.trading_date for order in accessor._order_execute]

        return con
    else:
        con = order.stop_loss and price >= order.stop_loss_prices and order.is_filled and date not in [
            order.trading_date for order in accessor._order_execute]

        return con


def touch_stop_profit(order: Order, price: float, date:pd.Timestamp) -> bool:

    if order.is_long:
        con = order.stop_profit and price >= order.stop_profit_prices and order.is_filled and date not in [
            order.trading_date for order in accessor._order_execute]

        return con
    else:
        con = order.stop_profit and price <= order.stop_profit_prices and order.is_filled and date not in [
            order.trading_date for order in accessor._order_execute]

        return con


