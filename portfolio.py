from time import sleep
from typing import Callable, List
import asyncio
from tqdm import tqdm


import pandas as pd
import matplotlib.pyplot as plt
from pandas.tseries.offsets import BDay
from pandas.tseries.holiday import USFederalHolidayCalendar
from pandas.tseries.offsets import CustomBusinessDay

from alphabt.strategy import Strategy
from alphabt.backtest import Backtest
from alphabt.statistic import index_accumulate_return

US_BUSINESS_DAY = CustomBusinessDay(calendar=USFederalHolidayCalendar())


class StrategyPort:
    """Compare the performance between different strategies"""

    def __init__(self, strategy_list: List[Strategy]):
        self.strategy_list = strategy_list

    def run(self, commission: int = None, plot: bool = False):
        report = pd.DataFrame()
        for s in self.strategy_list:
            _, per = Backtest(strategy=s, commission=commission).run()
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
    """Backtest the strategy with different stocks
    """
    def __init__(self, strategy_class: Strategy, data: pd.DataFrame):
        self.strategy = strategy_class
        self.multi_stock_data = data

        self.ticker_log_list = None

    def run(self) -> None:
        self.ticker_log_list = dict()
        for ticker in tqdm(self.multi_stock_data.symbol.unique()):
            try:
                sub_data = self.multi_stock_data[self.multi_stock_data.symbol.isin([ticker])]
                bt = Backtest(strategy=self.strategy(data=sub_data))
                bt.run()
                report, per = bt.get_report(print_sharpe=False)
                self.ticker_log_list[ticker] = report["累積報酬率(%)"]
                
            except Exception as e:
                print(e)
                continue
    
    def get_plot(self, size=(10, 15)) -> None:
        plt.figure(figsize=size)

        pd.DataFrame(self.ticker_log_list).plot()
        


class AsyncPortfolioBt:

    def __init__(self, strategy_class, data) -> None:
        self.strategy = strategy_class
        self.multi_stock_data = data

    async def _bt(self, ticker):
        sub_data = self.multi_stock_data[self.multi_stock_data.symbol.isin([ticker])]
        log = Bt(strategy=self.strategy(data=sub_data)).run()
        log['symbol'] = [ticker] * len(log)
        # await asyncio.sleep(0.5)
        return log

    
    async def main(self) :
        tasks=[self._bt(t) for t in self.multi_stock_data.symbol.unique()]
        res = await asyncio.gather(*tasks, return_exceptions=False)
        return res

    def run(self): 

        res = asyncio.run(self.main())

        log_res = pd.concat(res, 0)
        # log_res = log_res[['BuyDate', 'BuyPrice', 'SellDate', 'SellPrice', 'KeepDay', '報酬率(%)', 'symbol']]
        log_res = log_res.sort_values(by=['symbol', 'SellDate']).reset_index(drop=True).set_index(['symbol', log_res.index])
        
        return log_res


