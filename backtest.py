from numba import jit
import pandas as pd

from plot import get_plotly
from broker import *
from alphabt import util
from alphabt.strategy import Strategy
import statistic



class Bt:
    def __init__(self, strategy, commission=None):
        self.com = commission
        if isinstance(strategy, Strategy):
            self.Strategy = strategy
        else:
            self.Strategy = strategy()

        self.data = util.reset_data(self.Strategy.data)
            
        self.Broker = Broker(self.Strategy.init_capital)



    def run(self, benchmark='^GSPC', print_sharpe=True):

        self._back_test_loop(len(self.data), self.data.values, self.data.index, self.Strategy, self.Broker, self.com)

        # clean the last position
        if self.Strategy.position != 0:
            self.Broker.liquidation(pos=self.Strategy.position, price=self.data.values[-1, :], date=self.data.index[-1]
                                    , commission=self.com)

        record = self.Broker.get_log()

        report, performance = Report(self.data, record, self.Strategy.init_capital, print_sharpe).result(benchmark)

        return report, performance

    def get_plot(self, subplot_technical_index: list = None, overlap=None, sub_plot_param=None, overlap_param=None,
                 log=None, callback=None):
        get_plotly(self.data, subplot_technical_index, overlap=overlap, sub_plot_param=sub_plot_param
                   , overlap_param=overlap_param, log=log, callback=callback)
        
    @jit
    def _back_test_loop(self, data_length, data_values: np.array, data_index: pd.Timestamp, 
                    strategy_class: Strategy, broker_class: Broker, com: Union[None, float]) -> None:
        
        for i in range(1, data_length - 1):
            ohlc = data_values[i + 1, :4]
            strategy_class.signal(i)
            broker_class.check_order(ohlc, date=data_index[i + 1], commission=com)


class Report:
    def __init__(self, df, log_df, init_capital, print_sharpe: bool):
        self.df = df
        self.log = log_df
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
        record_df = self.log.copy()

        out_put = pd.DataFrame()
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
            out_put = pd.concat([out_put, performance_df])

        out_put['年化報酬率(%)'] = statistic.geo_yearly_ret(out_put)
        out_put['權益年化報酬率(%)'] = statistic.geo_yearly_ret(out_put, field='權益累積年度報酬(%)')
        # if there are market index data
        try:
            market_yearly_return = statistic.index_geo_yearly_ret(self.df, index=benchmark)

            out_put = pd.concat([out_put, market_yearly_return], 1)
        except:
            print(f'There is no {benchmark} data ')

        if self.print:
            util.print_result(sharpe=statistic.year_sharpe(out_put), calmar=statistic.calmar_ratio(out_put, record_df))

        return out_put

    def result(self, benchmark):
        return self.report(), self.yearly_performance(benchmark)



