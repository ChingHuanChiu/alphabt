from typing import Optional

import pandas as pd

from alphabt import util
from alphabt.common import statistic



class Report:
    def __init__(self, 
                 data: pd.DataFrame, 
                 log_df: pd.DataFrame, 
                 init_capital: float, 
                 print_sharpe: bool) -> None:

        self.data = data
        self.log = log_df
        self.init_cap = init_capital
        self.print = print_sharpe


    def get_trading_report(self) -> Optional[pd.DataFrame]:
        
        trading_df = self.log

        if trading_df.empty:
            return None

        trading_df['DurationDate'] = (trading_df['ExitDate'] - trading_df['EntryDate']).dt.days
        trading_df['profit($)'] = statistic.get_profit(trading_df)
        trading_df['ROI(%)'] = statistic.get_roi(trading_df)
        trading_df['AccumulateROI(%)'] = statistic.get_accumulate_roi(trading_df)
        trading_df['MDD(%)'] = statistic.mdd(self.data, trading_df)
        trading_df['EquityReturn'] = statistic.equity_return(trading_df, self.init_cap)
        trading_df['EquityAccumulateReturn'] = \
            round((((trading_df['EquityReturn'] * 0.01) + 1).cumprod() - 1) * 100, 3)
        return trading_df


    def get_yearly_report(self, 
                          benchmark: str,
                          trading_report: pd.DataFrame) -> pd.DataFrame:


        out_put_list = []
        count = 0
        for y in trading_report['ExitDate'].dt.year.unique():

            performance_df = pd.DataFrame()

            record_df_year = trading_report[trading_report['ExitDate'].dt.year == y]
            performance_df['年度總損益(元)'] = statistic.annual_profit(record_df_year)
            performance_df['作多次數(次)'] = statistic.long_times(record_df_year)
            performance_df['作空次數(次)'] = statistic.short_times(record_df_year)
            performance_df['交易總次數(次)'] = performance_df['作空次數(次)'] + performance_df['作多次數(次)']
            performance_df['勝率(%)'] = statistic.win_rate(record_df_year)
            performance_df['獲利因子'] = statistic.profit_factor(record_df_year)
            performance_df['最大損失(元)'] = statistic.max_loss(record_df_year)
            performance_df['最大獲利(元)'] = statistic.max_profit(record_df_year)
            performance_df['個股年度報酬(%)'] = statistic.stock_year_return(self.data, y)
            performance_df['當年度報酬率(%)'] = statistic.year_return(record_df_year, field='ROI(%)')
            performance_df['平均交易報酬率(%)'] = statistic.average_trade_return(performance_df)

            count += len(record_df_year)
            performance_df['累積年度報酬(%)'] = statistic.cum_year_return(trading_report, count, field='ROI(%)')
            performance_df['當年度權益報酬率(%)'] = statistic.year_return(record_df_year, field='EquityReturn')
            performance_df['權益累積年度報酬(%)'] = statistic.cum_year_return(trading_report, count, field='EquityReturn')
            performance_df['權益'] = round(trading_report['Equity'][count - 1])

            performance_df.index = [y]
            out_put_list.append(performance_df)

        out_put = pd.concat(out_put_list)

        out_put['年化報酬率(%)'] = statistic.geo_yearly_ret(out_put)
        out_put['權益年化報酬率(%)'] = statistic.geo_yearly_ret(out_put, field='權益累積年度報酬(%)')
        
        # if there are market index data
        if benchmark:
            market_yearly_return = statistic.index_geo_yearly_ret(self.data, index=benchmark)

            out_put = pd.concat([out_put, market_yearly_return], 1)


        if self.print:
            util.print_result(sharpe=statistic.year_sharpe(out_put), calmar=statistic.calmar_ratio(out_put, trading_report))

        return out_put
