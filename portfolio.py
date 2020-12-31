from strategy import Strategy
from backtest import Bt
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from plot import get_plotly
from typing import Callable
import numpy as np
import pandas as pd
import time

# data = pd.read_pickle('sp500.pkl')
# data = data[data.symbol == 'AMD']


class Portfolio:
    def __init__(self, data, start_date, end_date):
        self.data = data
        self.start_date = pd.to_datetime(start_date)
        self.end_date = pd.to_datetime(end_date)

    def run(self, hold_days, strategy: Callable):
        """
        TODO fix the code
        """
        assert isinstance(hold_days, int), 'the type of hold_dates should be int.'

        dates = self._date_iter_periodicity()
        ret_output = pd.Series()
        log_df = pd.DataFrame()
        for sdate, edate in dates:
            weight = [0.5] * len(strategy(self.data, sdate))
            print('============================================================')
            ret_df = pd.DataFrame()
            for s, w in zip(strategy(self.data, sdate), weight):
                sdata = self.data[self.data.symbol == s]
                # print('----->', type(pd.to_datetime(sdate)), edate)
                # 配合alpha，訊號出現隔天才交易，所以要將買賣訊號的日期往前一天
                log = buy_and_hold(sdata, sdate - BDay(1), edate - BDay(1))[0]
                log['symbol'] = s
                sub_sdata = sdata[log['BuyDay'][0]: log['SellDay'][0]]
                ret_df[s] = sub_sdata['close'].pct_change()
                # print(log)
                print({'symbol': s, 'buy_date': log['BuyDay'][0], 'sell_date': log['SellDay'][0]})

                log['weight'] = [w]

                #  log = log[['BuyPrice', 'BuyDay', 'SellPrice', 'SellDay', 'KeepDay', 'symbol', 'weight']]

                log_df = pd.concat([log_df, log], 0)

            ret = ret_df.dot(weight)

            ret_output = pd.concat([ret_output, ret])

        ret_output = ret_output + 1
        ret_output[0] = 1
        cum_ret_result = round(ret_output.cumprod(), 3).dropna()

        cum_ret_result.plot()
        plt.xlabel('Date')
        plt.ylabel('port. return(%)')
        plt.title('Return')

        return log_df, self.portfolio_log(log_df)

    def _date_iter_periodicity(self):
        date = self.start_date
        while date < self.end_date:
            yield date, (date + BDay(self.hold_days))
            date += BDay(self.hold_days)

    @staticmethod
    def portfolio_log(log):
        ret, mdd = [], []
        df = pd.DataFrame(index=log.SellDay.unique())
        df.index.name = '換股日期'
        for d in log.groupby('SellDay'):
            ret.append(d[1]['報酬率(%)'].dot(d[1]['weight']))
            mdd.append(d[1]['MDD(%)'].dot(d[1]['weight']))
        df['報酬率(%)'] = ret
        df['累積報酬率(%)'] = (((1 + df['報酬率(%)'] * 0.01).cumprod()) - 1) * 100
        df['MDD(%)'] = mdd

        return df


def buy_and_hold(data, start_date, end_date):
    class Port(Strategy):
        def __init__(self):
            self.data = data
            self.init_capital = np.inf

        def signal(self, index):

            if (self.data.index == start_date) & self.empty_position:

                self.buy()

            if self.data.index == end_date & self.long_position:
                self.sell()

    log, per = Bt(Port).run()
    return log, per




