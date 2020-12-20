import numpy as np
import pandas as pd
from talib import abstract

def annual_profit(record_df_year):
    return [round((record_df_year['profit(元)'].sum()), 2)]


def buy_times(record_df_year):
    # return [round(len(record_df_year['BuyDay']))]
    return [round(len(record_df_year[record_df_year.BuyDate < record_df_year.SellDate]))]


def sell_times(record_df_year):
    # return [round(len(record_df_year['SellDay']))]
    return [round(len(record_df_year[record_df_year.BuyDate > record_df_year.SellDate]))]


def trade_times(record_df_year):
    return [round(len(record_df_year))]


def win_rate(record_df_year):
    return [round((len(record_df_year[record_df_year['profit(元)'] > 0]) / len(record_df_year)) * 100, 2)]


def profit_factor(record_df_year):
    profit = record_df_year[record_df_year['profit(元)'] > 0]['profit(元)'].sum()
    loss = -(record_df_year[record_df_year['profit(元)'] < 0]['profit(元)'].sum())

    if 0 != loss:
        pf = round(profit / loss, 2)
    else:
        pf = round(profit / 1e-06, 2)

    return [pf]


def max_loss(record_df_year):
    max_loss = round(record_df_year[record_df_year['profit(元)'] < 0]['profit(元)'].min(), 0)
    return [max_loss]


def stock_max_loss(data, year):
    max_loss = round((data[str(year)]['close'].min() - data[str(year)]['close'][0]), 2)
    return [max_loss]


def max_profit(record_df_year):
    mp = round(record_df_year[record_df_year['profit(元)'] > 0]['profit(元)'].max(), 0)
    return [mp]


def stock_max_profit(data, year):
    mp = round((data[str(year)]['close'].max() - data[str(year)]['close'][0]), 2)
    return [mp]


def year_return(record_df_year):
    year_ret = round(((((1 + record_df_year['return']).cumprod()) - 1) * 100), 2).to_list()[-1]
    return [year_ret]


def net_year_return(record_df_year, handling_fee, tax):
    year_ret = \
    round((((1 + record_df_year['return'] * (1 - (2 * handling_fee + tax))).cumprod() - 1) * 100), 2).to_list()[-1]
    return [year_ret]


def stock_year_return(data, year):
    '''
    the annual return of per stock, buy with the 'open' price on first day and
    sell with the 'close' price on last day  in a single year
    '''
    stock_year_ret = format((((data[str(year)]['close'][-1] / data[str(year)]['open'][0]) - 1) * 100), '.2f')
    return [stock_year_ret]


def average_trade_return(performance_df):
    ave_trade_ret = round(((performance_df['年度報酬率(%)'] * 0.01) / performance_df['交易總次數(次)']) * 100, 2)
    return ave_trade_ret


def cum_year_return(record_df, count):
    cum_year_ret = round(((1 + record_df['return']).cumprod()[count - 1] - 1) * 100, 2)
    return [cum_year_ret]


def cum_equity(record_df, count):
    cum_equity = round(record_df['profit(元)'].cumsum()[count - 1], 2)
    return [cum_equity]


def mdd(df, log):
    mdd_list = []

    for d in range(len(log)):
        start = log['BuyDate'][d]
        end = log['SellDate'][d]

        if start < end:
            dd = (df[start:end]['close'].cummax() - df[start:end]['close']).max() / df[start:end]['close'].max()

        elif start > end:
            dd = -(df[end:start]['close'].cummin() - df[end:start]['close']).min() / df[end:start]['close'].min()
        mdd_list.append(dd)

    return [round(x * 100, 3) for x in mdd_list]


def year_sharpe(df):
    # len_year = len(df.index)

    ret_year = df['年化報酬率(%)'].mean()
    std_year = df['年化報酬率(%)'].std()
    sharpe = (ret_year - 0.01) / std_year
    return sharpe


def cost(trading_df, buyunit, sellunit):
    return np.where(trading_df.SellDate > trading_df.BuyDate, trading_df.BuyPrice * buyunit,
                    trading_df.SellPrice * sellunit * -1)


def geo_yearly_ret(per):
    '''
    :return: 年化報酬率
    '''
    geo_ret_list = []
    cum_ret = list(1 + per['累積年度報酬(%)'] * 0.01)
    for i in range(len(per)):
        yearly_ret = pow(cum_ret[i], 1 / (i + 1)) - 1
        geo_ret_list.append(round(yearly_ret * 100, 2))
    return geo_ret_list


def index_cummulate_return(start, end, index='^GSPC'):
    data = pd.read_pickle('index_close.pkl')[start: end]
    cum_return = round(((1 + data.pct_change()).cumprod() - 1) * 100, 3)
    cum_return = cum_return[index]
    return cum_return


def index_geo_yearly_ret(df, per, index='^GSPC'):
    start = str(df.index[0].year)
    end = str(df.index[-1].year)

    cum_return = index_cummulate_return(start, end, index=index)
    cum_ret = 1 + (cum_return * 0.01)
    # print(cum_ret)
    year_len = int(end) - int(start) + 1

    geo_ret_dict = {}
    for i, y in zip(range(year_len), cum_ret.index.year.unique()):
        yearly_ret = pow(cum_ret[str(y)][-1], 1 / (i + 1)) - 1
        geo_ret_dict[y] = round(yearly_ret * 100, 2)
    # print(geo_ret_dict)
    res = []
    for j in per.index:
        res.append(geo_ret_dict[j])

    return res


def daily_equity(daily_log, init_cap):
    if init_cap is None:

        x = [1] * len(daily_log)
    else:
        x = [init_cap] * len(daily_log)

    return x


def realized_pl(trade, daily_log):
    x = np.zeros(len(daily_log))

    for i in range(1, len(daily_log)):

        if (daily_log['部位'].values[i] > 0) & (daily_log['部位'].values[i - 1] < 0):
            x[i] = trade[i - 1] - trade[i]
        elif (daily_log['部位'].values[i] <= 0) & (daily_log['部位'].values[i - 1] > 0):
            x[i] = trade[i] - trade[i - 1]
    return x


def indicator(data, name, timeperiod=None):
    data.columns = [i.lower() for i in data.columns]
    O = data.loc[:, 'open'].astype('float')
    H = data.loc[:, 'high'].astype('float')
    L = data.loc[:, 'low'].astype('float')
    C = data.loc[:, 'close'].astype('float')
    V = data.loc[:, 'volume'].astype('float')
    OHLCV = {'open': O, 'high': H, 'low': L, 'close': C, 'volume': V}

    ret = pd.DataFrame(index=data.index)
    if timeperiod is not None:
        for t in timeperiod:
            f = getattr(abstract, name)
            output_names = f.output_names
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
        f = getattr(abstract, name)
        output_names = f.output_names
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