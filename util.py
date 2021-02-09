import pandas as pd
from accessor import order_execute

def reset_data(dataframe: pd.DataFrame):
    dataframe.index = pd.to_datetime(dataframe.index)
    dataframe.columns = [c.lower() for c in dataframe.columns]
    dataframe = dataframe[['open', 'high', 'low', 'close', 'volume']]
    return dataframe


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
    print('calarm ratio', '|', calmar, '--------|')
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