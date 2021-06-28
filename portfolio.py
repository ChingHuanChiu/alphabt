from alphabt.strategy import Strategy
from alphabt.backtest import Bt
from alphabt.statistic import indicator, index_accumulate_return
from alphabt.accessor import *


import pandas as pd
from typing import Callable, List
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


class StrategyPort:
    def __init__(self, strategy_list):
        self.strategy_list = strategy_list

    def run(self, commission=None, plot=False):
        report = pd.DataFrame()
        for s in self.strategy_list:
            _, per = Bt(strategy=s, commission=commission).run()
            report[f'{s.__name__}_WinRate(%)'] = per['勝率(%)']
            report[f'{s.__name__}_PF'] = per['獲利因子']
            report[f'{s.__name__}_EquityYearReturn'] = per['權益年化報酬率(%)']

        try:
            report['SP500Year'] = per['大盤年化報酬率(%)']
        except:
            pass
        report = report.fillna(0)

        if plot:
            report.loc[:, report.columns.str.endswith('WinRate(%)')].plot()
            report.loc[:, report.columns.str.endswith('PF')].plot()
            report.loc[:, report.columns.str.endswith('EquityYearReturn')].plot()

        return report


class PortfolioBt:
    def __init__(self, strategy_class, data):
        self.strategy = strategy_class
        self.multi_stock_data = data

    def run(self):
        ticker_log_list = []
        for ticker in self.multi_stock_data.symbol.unique():
            try:
                sub_data = self.multi_stock_data[self.multi_stock_data.symbol.isin([ticker])]

                ticker_log = Bt(strategy=self.strategy(data=sub_data)).run(print_sharpe=False)[0]
                ticker_log['symbol'] = [ticker] * len(ticker_log)
                ticker_log_list.append(ticker_log)
            except Exception as e:
                print(e)
                continue
        log_res = pd.concat(ticker_log_list, 0)
#         log_res = log_res.sort_values(by='BuyDate')
        log_res = log_res[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'KeepDay', '報酬率(%)', 'symbol']]
        log_res = log_res.sort_values(by=['symbol', 'SellDate']).reset_index(drop=True).set_index(['symbol', log_res.index])
        return log_res




# class PortfolioBt:
#     def __init__(self, data, start_date, end_date):
#         self.data = data
#         self.start_date = start_date
#         self.end_date = end_date
#
#     def run(self, hold_days: int, strategy: Callable):
#
#         assert isinstance(hold_days, int), 'the type of hold_dates should be int.'
#
#         signal_dict = self._strategy_ticker_signal(strategy)  # {ticker: trading signal}
#
#         ret_output = pd.Series()
#         log_df = pd.DataFrame()
#         print('Start backtest ...')
#         for sdate, edate in self._date_iter_periodicity(hold_days=hold_days):
#             try:
#                 ret_df = pd.DataFrame()
#                 selected_ticker_list = self._selected_ticker(signal_dict, sdate)
#                 weight = [round(float(1 / len(selected_ticker_list)), 3)] * len(selected_ticker_list)
#
#                 for s, w in zip(selected_ticker_list, weight):
#                     sdata = self.data[self.data.symbol.isin([s])]
#
#                     # 配合alphabt，訊號出現隔天才交易，所以要將買賣訊號的日期往前一天
#                     print(f'there are {len(selected_ticker_list)} stocks selected')
#                     print("ticker:", s, "trading_date:", sdate - BDay(1), "==========>", "change_date:", edate)
#                     log = buy_and_hold(sdata, sdate - 1 * US_BUSINESS_DAY, edate - 1 * US_BUSINESS_DAY)[0]
#
#                     log['symbol'] = s
#                     sub_sdata = sdata[log['BuyDate'][0]: log['SellDate'][0]]
#                     ret_df[s] = sub_sdata['close'].pct_change()
#                     log['weight'] = [w]
#
#                     log_df = pd.concat([log_df, log], 0)
#             except:
#                 continue
#
#             ret = ret_df.dot(weight)
#
#             ret_output = pd.concat([ret_output, ret])
#         ret_output = ret_output + 1
#         ret_output[0] = 1
#         cum_ret_result = round(ret_output.cumprod(), 3).dropna()
#         self._plot(cum_ret_result=cum_ret_result)
#         return log_df[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'KeepDay', '報酬率(%)', 'symbol', 'weight']], \
#                self.portfolio_log(log_df)
#
#     def _strategy_ticker_signal(self, strategy):
#         d = {ticker: df for ticker, df in self.data.groupby('symbol') if ticker not in ['^IXIC', '^GSPC', '^DJI']}
#
#         signal_dict = {ticker: strategy(sub_data) for ticker, sub_data in d.items() if not sub_data.empty}
#         return signal_dict
#
#     def _selected_ticker(self, signal_dict, sdate):
#         result = []
#
#         for ticker, signal in signal_dict.items():
#             try:
#                 if signal.loc[sdate]:
#                     result.append(ticker)
#             except:
#                 continue
#         return result
#
#     def _date_iter_periodicity(self, hold_days):
#         date = self.start_date
#         # if the start date is not the business date
#         while pd.to_datetime(date) < pd.to_datetime(self.end_date):
#             date = self.data.loc[str(date):].index[0]
#             date = pd.to_datetime(date)
#             yield date, (date + BDay(hold_days))
#             date += BDay(hold_days)
#
#     @staticmethod
#     def portfolio_log(log):
#         ret, mdd = [], []
#         df = pd.DataFrame(index=log.SellDate.unique())
#         df.index.name = '換股日期'
#         for d in log.groupby('SellDate'):
#             ret.append(d[1]['報酬率(%)'].dot(d[1]['weight']))
#             mdd.append(d[1]['MDD(%)'].dot(d[1]['weight']))
#
#         df['報酬率(%)'] = ret
#         df['累積報酬率(%)'] = (((1 + df['報酬率(%)'] * 0.01).cumprod()) - 1) * 100
#         df['MDD(%)'] = mdd
#
#         return df
#
#     def _plot(self, cum_ret_result):
#         cum_ret_result.name = 'Portfolio'
#         index = index_accumulate_return(start=cum_ret_result.index[0], end=cum_ret_result.index[-1], index='^GSPC')
#
#         (1 + 0.01 * index).plot(label='SP500')
#         cum_ret_result.plot()
#         plt.xlabel('Date')
#         plt.ylabel('port. return(%)')
#         plt.title('Return')
#         plt.legend()
#
#
# def buy_and_hold(data, start_date, end_date):
#     class Port(Strategy):
#         def __init__(self):
#             self.data = data
#             self.init_capital = 1000000
#
#         def signal(self, ind):
#             if (self.data.index[ind] == start_date) & self.empty_position:
#                 self.buy()
#
#             if (self.data.index[ind] == end_date) & self.long_position:
#                 self.sell()
#
#     log_df, per = Bt(Port).run(print_sharpe=False)
#     return log_df, per
