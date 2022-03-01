from typing import List
import asyncio


from alphabt.strategy import Strategy
from alphabt.backtest import Bt
from alphabt.statistic import indicator, index_accumulate_return


import pandas as pd
from typing import Callable, List
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


class StrategyPort:
    """Compare the performance between different strategies"""

    def __init__(self, strategy_list: List[Strategy]):
        self.strategy_list = strategy_list

    def run(self, commission: int = None, plot: bool = False):
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


import time
class PortfolioBt:
    """Backtest the strategy with different stocks
    """
    def __init__(self, strategy_class: Strategy, data: pd.DataFrame):
        self.strategy = strategy_class
        self.multi_stock_data = data

    def run(self):
        ticker_log_list = []
        for ticker in self.multi_stock_data.symbol.unique():
            try:
                sub_data = self.multi_stock_data[self.multi_stock_data.symbol.isin([ticker])]
                t0 = time.time()

                ticker_log = Bt(strategy=self.strategy(data=sub_data)).run(print_sharpe=False)[0]
                print(time.time() - t0)
                ticker_log['symbol'] = [ticker] * len(ticker_log)
                ticker_log_list.append(ticker_log)
            except Exception as e:
                print(e)
                continue
        log_res = pd.concat(ticker_log_list, 0)
        log_res = log_res[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'KeepDay', '報酬率(%)', 'symbol']]
        log_res = log_res.sort_values(by=['symbol', 'SellDate']).reset_index(drop=True).set_index(['symbol', log_res.index])
        return log_res



class AsyncPortfolioBt:

    def __init__(self, strategy_class, data) -> None:
        self.strategy = strategy_class
        self.multi_stock_data = data

    async def _bt(self, ticker):
        sub_data = self.multi_stock_data[self.multi_stock_data.symbol.isin([ticker])]
        log = Bt(strategy=self.strategy(data=sub_data)).run(print_sharpe=False)[0]
        log['symbol'] = [ticker] * len(log)
        return log

    
    async def main(self) :

        tasks=[self._bt(t) for t in self.multi_stock_data.symbol.unique()]

        res = await asyncio.gather(*tasks, return_exceptions=False)

        log_res = pd.concat(res, 0)
        log_res = log_res[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'KeepDay', '報酬率(%)', 'symbol']]
        log_res = log_res.sort_values(by=['symbol', 'SellDate']).reset_index(drop=True).set_index(['symbol', log_res.index])
        
        return log_res


