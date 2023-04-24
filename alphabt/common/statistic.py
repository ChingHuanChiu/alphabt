from typing import List

import numpy as np
import pandas as pd
from talib import abstract


from data.data import Data

def get_profit(trading_log: pd.DataFrame) -> pd.Series:

    def _profit(data):
        res = data['ExitPrice'] - data['EntryPrice']

        if data['action'] == 'long':
            profit = res * data['unit']

        elif data['action'] == 'short':
            profit = -res * data['unit']
        return profit
        

    return trading_log.apply(lambda x: _profit(x), axis=1)


def get_roi(trading_log: pd.DataFrame) -> pd.Series:

    def _roi(data):
        if data['action'] == 'long':
            field = 'EntryPrice'
        elif data['action'] == 'short':
            field = 'ExitPrice'
            
        invest_cost = data[field]
        roi = (trading_log['profit($)'][0] / invest_cost) * 100

        return roi
    return trading_log.apply(lambda x: _roi(x), axis=1)


def get_accumulate_roi(trading_df: pd.DataFrame) -> pd.Series:

    return round((((trading_df['ROI(%)'] * 0.01) + 1).cumprod() - 1) * 100, 3)



def annual_profit(record_df_year):
    return [round((record_df_year['profit($)'].sum()), 2)]


def long_times(record_df_year):
    return [round(len(record_df_year[record_df_year.EntryDate < record_df_year.ExitDate]))]


def short_times(record_df_year):
    return [round(len(record_df_year[record_df_year.EntryDate > record_df_year.ExitDate]))]


def trade_times(record_df_year):
    return [round(len(record_df_year))]


def win_rate(record_df_year):
    return [round((len(record_df_year[record_df_year['profit($)'] > 0]) / len(record_df_year)) * 100, 2)]


def profit_factor(record_df_year):
    profit = record_df_year[record_df_year['profit($)'] > 0]['profit($)'].sum()
    loss = -(record_df_year[record_df_year['profit($)'] < 0]['profit($)'].sum())

    if loss != 0:
        pf = profit / loss
    else:
        pf = profit / 1e-06

    return [round(pf, 3)]


def equity_return(log, init_equity):
    first = (log.Equity[0] - init_equity) / init_equity
    return log.Equity.pct_change().fillna(value=first) * 100


def max_loss(record_df_year):
    max_loss = round(record_df_year[record_df_year['profit($)'] < 0]['profit($)'].min(), 0)
    if np.isnan(max_loss):
        max_loss = 0
    return [max_loss]


def stock_max_loss(data, year):
    max_loss = round((data[str(year)]['close'].min() - data[str(year)]['close'][0]), 2)
    return [max_loss]


def max_profit(record_df_year):
    mp = round(record_df_year[record_df_year['profit($)'] > 0]['profit($)'].max(), 0)
    if np.isnan(mp):
        mp = 0
    return [mp]


def stock_max_profit(data, year):
    mp = round((data[str(year)]['close'].max() - data[str(year)]['close'][0]), 2)
    return [mp]


def year_return(record_df_year, field: str):
    year_ret = round(((((1 + record_df_year[field]*0.01).cumprod()) - 1) * 100), 2).to_list()[-1]
    return [year_ret]


def stock_year_return(data, year):
    '''
    the annual return of per stock, buy with the 'open' price on first day and
    sell with the 'close' price on last day  in a single year
    '''
    stock_year_ret = format((((data[str(year)]['close'][-1] / data[str(year)]['open'][0]) - 1) * 100), '.2f')
    return [stock_year_ret]


def average_trade_return(performance_df):
    ave_trade_ret = round(((performance_df['當年度報酬率(%)'] * 0.01) / performance_df['交易總次數(次)']) * 100, 2)
    return ave_trade_ret


def cum_year_return(record_df, count, field: str):
    cum_year_ret = round(((1 + record_df[field]*0.01).cumprod()[count - 1] - 1) * 100, 2)
    return [cum_year_ret]


def cum_equity(record_df, count):
    cum_equity = round(record_df['profit($)'].cumsum()[count - 1], 2)
    return [cum_equity]


def mdd(df, log):
    """

    :param df: stock data with OHLCV
    :param log: trading log

    """
    mdd_list = []

    for d in range(len(log)):
        start = log['EntryDate'][d]
        end = log['ExitDate'][d]

        if start < end:
            dd = (df[start:end]['close'].cummax() - df[start:end]['close']).max() / df[start:end]['close'].max()

        elif start > end:
            dd = -(df[end:start]['close'].cummin() - df[end:start]['close']).min() / df[end:start]['close'].min()

        else:
            dd = 0

        mdd_list.append(dd)

    return [round(x * 100, 3) for x in mdd_list]


def year_sharpe(df):
    # len_year = len(df.index)

    ret_year = df['權益年化報酬率(%)'].values[-1]
    std_year = df['當年度權益報酬率(%)'].std()
    sharpe = (ret_year - 0.01) / std_year
    return round(sharpe, 3)


def calmar_ratio(per, log):
    ret_year = per['權益年化報酬率(%)'].values[-1]
    MDD = log['MDD(%)'].max()
    calmar = ret_year / MDD
    return round(calmar, 3)


def geo_yearly_ret(per, field='累積年度報酬(%)'):
    '''
    :return: 年化報酬率
    '''
    geo_ret_list = []
    cum_ret = list(1 + per[field] * 0.01)
    for i in range(len(per)):
        yearly_ret = pow(cum_ret[i], 1 / (i + 1)) - 1
        geo_ret_list.append(round(yearly_ret * 100, 2))
    return geo_ret_list


def index_accumulate_return(start, end, index='^GSPC'):
    Data.datasource = 'yfapi'
    data = Data().get_data(ticker=index, startdate=start, enddate=end)['close']
    cum_return = round(((1 + data.pct_change()).cumprod() - 1) * 100, 3)
    # cum_return = cum_return[index]
    return cum_return


def index_geo_yearly_ret(df, index='^GSPC'):
    start = str(df.index[0].year)
    end = str(df.index[-1].year)
    cum_return = index_accumulate_return(start, end, index=index)
    cum_ret = 1 + (cum_return * 0.01)
    year_len = int(end) - int(start) + 1

    geo_ret_dict = {}
    for i, y in zip(range(year_len), cum_ret.index.year.unique()):
        yearly_ret = pow(cum_ret[str(y)][-1], 1 / (i + 1)) - 1
        geo_ret_dict[y] = round(yearly_ret * 100, 2)

    return pd.DataFrame(list(geo_ret_dict.values()),
                        index=list(geo_ret_dict.keys()), columns=['大盤年化報酬率(%)'])


