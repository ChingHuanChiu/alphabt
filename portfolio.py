from strategy import Strategy
from backtest import Bt
from statistic import indicator
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from datetime import datetime
from typing import Callable
from data import Data
import pandas as pd


class Portfolio:
    def __init__(self, start_date, end_date):
        self.data = Data().data
        self.start_date = start_date
        self.end_date = end_date

    def run(self, hold_days: int, strategy: Callable):
        """
        TODO fix the code
        """
        assert isinstance(hold_days, int), 'the type of hold_dates should be int.'

        # dates = self._date_iter_periodicity(hold_days=hold_days)
        signal_dict = self._strategy_ticker_signal(strategy)  # {ticker: }

        ret_output = pd.Series()
        log_df = pd.DataFrame()

        for sdate, edate in self._date_iter_periodicity(hold_days=hold_days):
            ret_df = pd.DataFrame()
            selected_ticker_list = self._selected_ticker(signal_dict, sdate)
            weight = [0.5] * len(selected_ticker_list)

            for s, w in zip(selected_ticker_list, weight):
                sdata = self.data[self.data.symbol == s]

                # 配合alpha，訊號出現隔天才交易，所以要將買賣訊號的日期往前一天
                print(s, sdate, edate,'---------------',sdate - BDay(1))
                log = buy_and_hold(sdata, sdate - BDay(1), edate - BDay(1))[0]

                log['symbol'] = s
                sub_sdata = sdata[log['BuyDate'][0]: log['SellDate'][0]]
                ret_df[s] = sub_sdata['close'].pct_change()
                # print({'symbol': s, 'buy_date': log['BuyDate'][0], 'sell_date': log['SellDate'][0]})

                log['weight'] = [w]

                #  log = log[['BuyPrice', 'BuyDay', 'SellPrice', 'SellDay', 'KeepDay', 'symbol', 'weight']]

                log_df = pd.concat([log_df, log], 0)

            ret = ret_df.dot(weight)

            ret_output = pd.concat([ret_output, ret])
        print(ret_output)
        ret_output = ret_output + 1
        ret_output[0] = 1
        cum_ret_result = round(ret_output.cumprod(), 3).dropna()

        cum_ret_result.plot()
        plt.xlabel('Date')
        plt.ylabel('port. return(%)')
        plt.title('Return')

        return log_df, self.portfolio_log(log_df)

    def _strategy_ticker_signal(self, strategy):
        d = {ticker: df for ticker, df in data.groupby('symbol')}
        signal_dict = {ticker: strategy(sub_data) for ticker, sub_data in d.items()}
        return signal_dict

    def _selected_ticker(self, signal_dict, sdate):
        result = []

        for ticker, signal in signal_dict.items():
            try:
                if signal.loc[sdate]:
                    result.append(ticker)
            except:
                continue
        return result

    def _date_iter_periodicity(self, hold_days):
        date = self.start_date
        # if the start date is not the business date
        while pd.to_datetime(date) < pd.to_datetime(self.end_date):
            date = self.data.loc[date:].index[0]
            date = pd.to_datetime(date)
            # print('----------->', date)
            yield date, (date + BDay(hold_days))
            date += BDay(hold_days)

    @staticmethod
    def portfolio_log(log):
        ret, mdd = [], []
        df = pd.DataFrame(index=log.SellDate.unique())
        df.index.name = '換股日期'
        for d in log.groupby('SellDate'):
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
            self.init_capital = 1000000

        def signal(self, ind):
            # print(self.data.index[ind], start_date, self.data.index[ind] == start_date)#, self.data.index[ind] == end_date)
            if (self.data.index[ind] == start_date) & self.empty_position:
                self.buy(unit=1)

            if (self.data.index[ind] == end_date) & self.long_position:
                self.sell()

    log, per = Bt(Port).run()
    return log, per

if __name__ == '__main__':

    data = pd.read_pickle('sp500.pkl')
    data.columns = [c.lower() for c in data.columns]

    def strategy(df):

        kd = indicator(df, 'STOCH')
        # std = indicator(data, 'STDDEV')
        condition = (kd['slowk'] > kd['slowd']) & (kd['slowk'].shift() < kd['slowd'].shift())
        # condition = (std['STDDEV'] > 1)  # & (cci['STDDEV'].shift(1) < -100)
        return condition

    log, pot_log = Portfolio(start_date='2010-01-10', end_date='2012-01-01').run(hold_days=120, strategy=strategy)
