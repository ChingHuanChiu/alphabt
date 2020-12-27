import pandas as pd
import statistic
from plot import get_plotly
from broker import *


class Bt:
    def __init__(self, strategy):
        # self.data = data

        self.Strategy = strategy()
        self.data = self.Strategy.data
        self.Broker = Broker(self.Strategy.init_capital)

    def run(self):
        for i in range(1, len(self.data) - 1):
            
            self.Strategy.signal(i)
            self.Broker.check_order(self.data.iloc[i + 1, :], date=self.data.index[i + 1])

            self.Broker.work(self.data.iloc[i + 1, :], date=self.data.index[i + 1])

        if self.Strategy.position != 0:

            self.Broker.liquidation(pos=self.Strategy.position, price=self.data.iloc[-1, :], date=self.data.index[-1])

        record = self.Broker.get_log()

        report, performance = Report(self.data, record, self.Strategy.init_capital).result()

        return report, performance

    def get_plot(self, subplot_technical_index: list, overlap=None, sub_plot_param=None, overlap_param=None, log=None):
        get_plotly(self.data, subplot_technical_index, overlap=overlap, sub_plot_param=sub_plot_param
                   , overlap_param=overlap_param, log=log)


class Report:
    def __init__(self, df, log_df, init_capital):
        self.df = df
        self.log = log_df
        self.init_cap = init_capital

    def report(self):
        trading_df = self.log

        assert trading_df.empty != True, 'Your Strategy may have no sell(buy) signal!!'

        trading_df['SellDate'] = pd.to_datetime(trading_df['SellDate'])
        trading_df['BuyDate'] = pd.to_datetime(trading_df['BuyDate'])
        trading_df['KeepDay'] = (trading_df['SellDate'] - trading_df['BuyDate']).dt.days
        trading_df['profit(元)'] = trading_df['SellPrice'] * trading_df['SellUnits'] * -1 - trading_df['BuyPrice'] * \
                                  trading_df['BuyUnits']

        trading_df['成本'] = statistic.cost(trading_df, trading_df['BuyUnits'], trading_df['SellUnits'])
        trading_df['報酬率(%)'] = round(
            ((trading_df['profit(元)']) / trading_df['成本']) * 100, 3)
        trading_df['累積報酬率(%)'] = round((((trading_df['報酬率(%)'] * 0.01) + 1).cumprod() - 1) * 100, 3)
        trading_df['MDD(%)'] = statistic.mdd(self.df, trading_df)

        if self.init_cap:
            trading_df['累計淨值(元)'] = self.init_cap * (1 + (0.01 * trading_df['累積報酬率(%)']))

        return trading_df

    def yearly_performance(self):
        record_df = self.log.copy()

        record_df['return'] = record_df['報酬率(%)'] / 100

        out_put = pd.DataFrame()
        count = 0
        for y in record_df['SellDate'].dt.year.unique():

            performance_df = pd.DataFrame()

            record_df_year = record_df[record_df['SellDate'].dt.year == y]
            performance_df['年度總損益(元)'] = statistic.annual_profit(record_df_year)
            performance_df['作多次數(次)'] = statistic.buy_times(record_df_year)
            performance_df['作空次數(次)'] = statistic.sell_times(record_df_year)
            performance_df['交易總次數(次)'] = statistic.trade_times(record_df_year)
            performance_df['勝率(%)'] = statistic.win_rate(record_df_year)
            performance_df['獲利因子'] = statistic.profit_factor(record_df_year)
            performance_df['最大損失(元)'] = statistic.max_loss(record_df_year)
            # performance_df['個股年度最大損失(元)'] = statistic.stock_max_loss(self.df, y)
            performance_df['最大獲利(元)'] = statistic.max_profit(record_df_year)
            # performance_df['個股年度最大獲利(元)'] = statistic.stock_max_profit(self.df, y)
            performance_df['個股年度報酬(%)'] = statistic.stock_year_return(self.df, y)
            # performance_df['年度報酬率(%)'] = statistic.year_return(record_df_year)
            # performance_df['平均交易報酬率(%)'] = statistic.average_trade_return(performance_df)

            count += len(record_df_year)
            performance_df['累積年度報酬(%)'] = statistic.cum_year_return(record_df, count)

            # performance_df['年度淨報酬率(%)'] = statistic.net_year_return(record_df_year, self.handling_fee, self.tax)
            if self.init_cap:
                performance_df['累計淨值(元)'] = round(record_df['累計淨值(元)'][count - 1])
            else:
                performance_df['累計淨值(元)'] = statistic.cum_equity(record_df, count)

            performance_df.index = [y]
            out_put = pd.concat([out_put, performance_df])

        # print(out_put)
        out_put['年化報酬率(%)'] = statistic.geo_yearly_ret(out_put)
#         out_put['大盤年化報酬率(%)'] = statistic.index_geo_yearly_ret(self.df, out_put, index='^GSPC')
        print('Sharpe Ratio is :', statistic.year_sharpe(out_put))
        return out_put

    def result(self):
        return self.report(), self.yearly_performance()


if __name__ == '__main__':
    from strategy import Strategy
    from backtest import Bt
    import matplotlib.pyplot as plt
    from plot import get_plotly

    import pandas as pd
    import time

    data = pd.read_pickle('sp500.pkl')
    data = data[data.symbol == 'AMD']
    class CCI(Strategy):
        def __init__(self):
            self.data = data
            self.init_capital = 100000
            self.cci = self.indicator('CCI')

        #         print(self.position)
        def signal(self, index):

            if (self.cci['CCI'][index] > -100) & (self.cci['CCI'][index - 1] < -100) & self.empty_position:
                # self.close_position()
                self.buy(unit=0.2)
            if (self.cci['CCI'][index] < 100) & (self.cci['CCI'][index - 1] > 100) & self.long_position:
                # self.close_position()
                self.sell()


    import time

    s = time.time()
    log, per = Bt(CCI).run()
    e = time.time()
    print(e - s)