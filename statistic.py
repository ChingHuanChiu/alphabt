import numpy as np
import pandas as pd
from talib import abstract
from typing import List

from alphabt.data import Data


def annual_profit(record_df_year):
    return [round((record_df_year['profit(元)'].sum()), 2)]


def buy_times(record_df_year):
    return [round(len(record_df_year[record_df_year.BuyDate < record_df_year.SellDate]))]


def sell_times(record_df_year):
    return [round(len(record_df_year[record_df_year.BuyDate > record_df_year.SellDate]))]


def trade_times(record_df_year):
    return [round(len(record_df_year))]


def win_rate(record_df_year):
    return [round((len(record_df_year[record_df_year['profit(元)'] > 0]) / len(record_df_year)) * 100, 2)]


def profit_factor(record_df_year):
    profit = record_df_year[record_df_year['profit(元)'] > 0]['profit(元)'].sum()
    loss = -(record_df_year[record_df_year['profit(元)'] < 0]['profit(元)'].sum())

    if loss != 0:
        pf = profit / loss
    else:
        pf = profit / 1e-06

    return [round(pf, 3)]


def equity(log, init_equity):
    eq = log['profit(元)'].cumsum() + init_equity
    return eq


def equity_return(log, init_equity):
    first = (log.Equity[0] - init_equity) / init_equity
    return log.Equity.pct_change().fillna(value=first) * 100


def max_loss(record_df_year):
    max_loss = round(record_df_year[record_df_year['profit(元)'] < 0]['profit(元)'].min(), 0)
    if np.isnan(max_loss):
        max_loss = 0
    return [max_loss]


def stock_max_loss(data, year):
    max_loss = round((data[str(year)]['close'].min() - data[str(year)]['close'][0]), 2)
    return [max_loss]


def max_profit(record_df_year):
    mp = round(record_df_year[record_df_year['profit(元)'] > 0]['profit(元)'].max(), 0)
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
    cum_equity = round(record_df['profit(元)'].cumsum()[count - 1], 2)
    return [cum_equity]


def mdd(df, log):
    """

    :param df: stock data with OHLCV
    :param log: trading log

    """
    mdd_list = []

    for d in range(len(log)):
        start = log['BuyDate'][d]
        end = log['SellDate'][d]

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
    data = Data().get(symbol=[index], date_range=(start, end))['close']
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


def indicator(data, name: str, timeperiod: List[int] = None):
    """

    :param data: stock data with "close", "open", "high", "low", "volume"
    :param name: function name of TA-Lib package
    :param timeperiod: parameter of TA-Lib method
    :return:
    """

    OHLCV = {'open':   data['open'],
             'high':   data['high'],
             'low':    data['low'],
             'close':  data['close'],
             'volume': data['volume']
             }

    ret = pd.DataFrame(index=data.index)
    f = getattr(abstract, name)
    output_names = f.output_names

    if timeperiod is not None:
        for t in timeperiod:

            s = f(OHLCV, timeperiod=t)
            s = pd.to_numeric(s, errors='coerce')

            if len(output_names) == 1:
                dic = s
                s_df = pd.DataFrame(dic, index=data.index,
                                    columns=['{}'.format(t) + name])  # 當output_names=1時，s為array
            else:
                s = s.T
                output_names_col = [f'{n}_{str(t)}' for n in output_names]
                s_df = pd.DataFrame(s, index=data.index, columns=output_names_col)  # 當output_names>1時，s為list
            ret = pd.concat([ret, s_df], axis=1)
    else:

        s = f(OHLCV)
        s = pd.to_numeric(s, errors='coerce')
        if len(output_names) == 1:
            dic = s
            s_df = pd.DataFrame(dic, index=data.index, columns=[name])
        else:
            s = s.T
            s_df = pd.DataFrame(s, index=data.index, columns=output_names)

        ret = pd.concat([ret, s_df], axis=1)
    return ret




