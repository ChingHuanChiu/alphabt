import pandas as pd
import numpy as np
from action import Trading
import statistic


class Report:
    def __init__(self, df, init_cap, stop_loss, handling_fee, tax, sell_short, trading_unit):
        self.df = df
        self.init_cap = init_cap
        self.stop_loss = stop_loss
        self.handling_fee = handling_fee
        self.tax = tax
        self.sell_short = sell_short
        self.trading_unit = trading_unit

        self.log_data, self.pos = Trading(self.df, self.stop_loss, self.sell_short).process_trading(self.trading_unit)

    def log(self):
        trading_df = pd.DataFrame(self.log_data)

        assert trading_df.empty != 'True', 'Your Strategy may have no sell(buy) signal!!'

        trading_df['SellDay'] = pd.to_datetime(trading_df['SellDay'])
        trading_df['BuyDay'] = pd.to_datetime(trading_df['BuyDay'])
        trading_df['KeepDay'] = (trading_df['SellDay'] - trading_df['BuyDay']).dt.days
        trading_df['成本'] = statistic.cost(trading_df, self.trading_unit)
        trading_df['profit(元)'] = (trading_df['SellPrice'] - trading_df['BuyPrice']) * self.trading_unit
        trading_df['報酬率(%)'] = round(
            ((trading_df['profit(元)']) / trading_df['成本']) * 100 * (1 - (2 * self.handling_fee + self.tax)), 3)
        trading_df['累積報酬率(%)'] = round((((trading_df['報酬率(%)'] * 0.01) + 1).cumprod() - 1) * 100, 3)
        trading_df['MDD(%)'] = statistic.mdd(self.df, trading_df)

        if self.init_cap:
            trading_df['累計淨值(元)'] = self.init_cap * (1 + (0.01 * trading_df['累積報酬率(%)']))

        return trading_df

    def yearly_performance(self):
        record_df = self.log().copy()
        record_df['return'] = record_df['報酬率(%)'] / 100

        out_put = pd.DataFrame()
        count = 0
        for y in record_df['SellDay'].dt.year.unique():
            performance_df = pd.DataFrame()

            record_df_year = record_df[record_df['SellDay'].dt.year == y]
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
        out_put['年化報酬率(%)'] = statistic.geo_yearly_ret(out_put)
        out_put['大盤年化報酬率(%)'] = statistic.index_geo_yearly_ret(self.df, out_put, index='^GSPC')
        print('Sharpe Ratio is :', statistic.year_sharpe(out_put))
        return out_put

    def get_report(self):
        return self.log(), self.yearly_performance().T

    def get_daily_log(self):
        daily_log = pd.DataFrame(index=self.df.index)

        buy = pd.Series(self.log()['BuyPrice'].values, index=self.log()['BuyDay']).drop_duplicates().rename('買進價格')
        sell = pd.Series(self.log()['SellPrice'].values, index=self.log()['SellDay']).drop_duplicates().rename('賣出價格')
        daily_log = pd.concat([buy, sell, daily_log], 1)
        # _trade = daily_log['買進價格'].fillna(0) + daily_log['賣出價格']
        _trade = pd.concat([buy, sell], 0).reindex(self.df.index)

        _trade = _trade.ffill()

        daily_log['部位'] = self.pos
        daily_log['部位狀態'] = np.where(daily_log['部位'] > 0, '多方', '空方')
        daily_log['部位狀態'] = np.where(daily_log['部位'] == 0, '空手', daily_log['部位狀態'])

        daily_log['未實現損益'] = (self.df['close'] - _trade) * daily_log['部位']
        daily_log['未實現損益'] = daily_log['未實現損益'].fillna(value=0)

        daily_log['實現損益'] = statistic.realized_pl(_trade, daily_log)

        daily_ret_unrealize = daily_log['未實現損益'] / _trade
        daily_ret_realize = (daily_log['實現損益'] / (_trade.fillna(1).shift()) + 1).cumprod() - 1
        daily_ret = (1 + daily_ret_realize) * (1 + daily_ret_unrealize)

        daily_log['淨值'] = statistic.daily_equity(daily_log, self.init_cap) * daily_ret

        return daily_log



