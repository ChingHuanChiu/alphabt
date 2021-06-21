import pandas as pd
from numba import jit

from alphabt.accessor import order_execute


def reset_data(data_frame: pd.DataFrame):
    data_frame.index = pd.to_datetime(data_frame.index)
    data_frame.columns = [c.lower() for c in data_frame.columns]
    data_frame = data_frame[['open', 'high', 'low', 'close', 'volume', 'symbol']]
    return data_frame


def adjust_price(trade, commission):
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


def print_result(sharpe, calmar):
    print('-----------------------------|')
    print('sharpe ratio', '|', sharpe, '--------|')
    print('-----------------------------|')
    print('calmar ratio', '|', calmar, '--------|')
    print('-----------------------------|')


def touch_stop_loss(order, price, date):

    if order.is_long:
        con = order.stop_loss and price <= order.stop_loss_prices and order.is_filled and date not in [
            order.trading_date for order in order_execute]

        return con
    else:
        con = order.stop_loss and price >= order.stop_loss_prices and order.is_filled and date not in [
            order.trading_date for order in order_execute]

        return con


def touch_stop_profit(order, price, date):

    if order.is_long:
        con = order.stop_profit and price >= order.stop_profit_prices and order.is_filled and date not in [
            order.trading_date for order in order_execute]

        return con
    else:
        con = order.stop_profit and price <= order.stop_profit_prices and order.is_filled and date not in [
            order.trading_date for order in order_execute]

        return con


@jit
def back_test_loop(data_length, data_values, data_index, strategy_class, broker_class, com):
    for i in range(1, data_length - 1):
        ohlc = data_values[i + 1, :4]
        strategy_class.signal(i)
        broker_class.check_order(ohlc, date=data_index[i + 1], commission=com)