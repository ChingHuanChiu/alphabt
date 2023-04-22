import pandas as pd

from alphabt import util
import statistic




class Report:
    def __init__(self, df, log_df, init_capital, print_sharpe: bool):
        self.df = df
        self.log = log_df.copy()
        self.init_cap = init_capital
        self.print = print_sharpe

    def report(self):
        trading_df = self.log

        assert trading_df.empty is not True, 'Your Strategy may have no sell(buy) signal!!'

        trading_df['KeepDay'] = (trading_df['SellDate'] - trading_df['BuyDate']).dt.days
        trading_df['profit(元)'] = trading_df.CashReceiving - trading_df.CashPaying
        trading_df['報酬率(%)'] = round((trading_df.CashReceiving / trading_df.CashPaying - 1) * 100, 3)
        trading_df['累積報酬率(%)'] = round((((trading_df['報酬率(%)'] * 0.01) + 1).cumprod() - 1) * 100, 3)
        trading_df['MDD(%)'] = statistic.mdd(self.df, trading_df)
        trading_df['Equity'] = statistic.equity(trading_df, self.init_cap)
        trading_df['EquityReturn'] = statistic.equity_return(trading_df, self.init_cap)
        trading_df['EquityAccumulateReturn'] = round((((trading_df['EquityReturn'] * 0.01) + 1).cumprod() - 1) * 100, 3)
        return trading_df

    def yearly_performance(self, benchmark):
        record_df = self.log

        out_put_list = []
        count = 0
        for y in record_df['SellDate'].dt.year.unique():

            performance_df = pd.DataFrame()

            record_df_year = record_df[record_df['SellDate'].dt.year == y]
            performance_df['年度總損益(元)'] = statistic.annual_profit(record_df_year)
            performance_df['作多次數(次)'] = statistic.buy_times(record_df_year)
            performance_df['作空次數(次)'] = statistic.sell_times(record_df_year)
            performance_df['交易總次數(次)'] = performance_df['作空次數(次)'] + performance_df['作多次數(次)']
            performance_df['勝率(%)'] = statistic.win_rate(record_df_year)
            performance_df['獲利因子'] = statistic.profit_factor(record_df_year)
            performance_df['最大損失(元)'] = statistic.max_loss(record_df_year)
            performance_df['最大獲利(元)'] = statistic.max_profit(record_df_year)
            performance_df['個股年度報酬(%)'] = statistic.stock_year_return(self.df, y)
            performance_df['當年度報酬率(%)'] = statistic.year_return(record_df_year, field='報酬率(%)')
            performance_df['平均交易報酬率(%)'] = statistic.average_trade_return(performance_df)

            count += len(record_df_year)
            performance_df['累積年度報酬(%)'] = statistic.cum_year_return(record_df, count, field='報酬率(%)')
            performance_df['當年度權益報酬率(%)'] = statistic.year_return(record_df_year, field='EquityReturn')
            performance_df['權益累積年度報酬(%)'] = statistic.cum_year_return(record_df, count, field='EquityReturn')
            performance_df['權益'] = round(record_df['Equity'][count - 1])

            performance_df.index = [y]
            out_put_list.append(performance_df)

        out_put = pd.concat(out_put_list)

        out_put['年化報酬率(%)'] = statistic.geo_yearly_ret(out_put)
        out_put['權益年化報酬率(%)'] = statistic.geo_yearly_ret(out_put, field='權益累積年度報酬(%)')
        
        # if there are market index data
        if benchmark:
            market_yearly_return = statistic.index_geo_yearly_ret(self.df, index=benchmark)

            out_put = pd.concat([out_put, market_yearly_return], 1)


        if self.print:
            util.print_result(sharpe=statistic.year_sharpe(out_put), calmar=statistic.calmar_ratio(out_put, record_df))

        return out_put

    def result(self, benchmark):
        return self.report(), self.yearly_performance(benchmark)