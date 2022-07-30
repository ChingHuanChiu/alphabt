from typing import Tuple


import pandas as pd


from plot import get_plotly
from broker import *
from alphabt import util
from alphabt.strategy import Strategy, Equity
from alphabt.accessor import Accessor
from alphabt.report import Report



class Backtest:
    def __init__(self, strategy, commission=None) -> None:

        Accessor.initial()
        self.com = commission
        if isinstance(strategy, Strategy):
            self.Strategy = strategy
        else:
            self.Strategy = strategy()

        self.data = util.reset_data(self.Strategy.data)
        self.Broker = Broker(Equity(self.Strategy.init_capital), commission=self.com)


    
    def run(self) -> None:
        self._back_test_loop(len(self.data), self.data.values, self.data.index, self.Strategy, self.Broker)

        # clean the last position
    
        if self.Strategy.position != 0:
            self.Broker.liquidation(pos=self.Strategy.position, price=self.data.values[-1, :], date=self.data.index[-1] )


    def get_report(self, benchmark='^GSPC', print_sharpe=True) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Get the trading report and yearly report from trading log
        """
        trading_log = self.Broker.get_log()
        report, performance = Report(self.data, trading_log, self.Strategy.init_capital, print_sharpe).result(benchmark)
        return report, performance


    def get_plot(self, subplot_technical_index: list = None, overlap=None, sub_plot_param=None, overlap_param=None,
                 log=None, callback=None) -> None:
        get_plotly(self.data, subplot_technical_index, overlap=overlap, sub_plot_param=sub_plot_param
                   , overlap_param=overlap_param, log=log, callback=callback)
        
    
    def _back_test_loop(self, data_length, data_values: np.array, data_index: pd.Timestamp, 
                    strategy_class: Strategy, broker_class: Broker) -> None:
        
        for i in range(1, data_length - 1):
            ohlc = data_values[i + 1, :4]
            strategy_class.signal(i)
            broker_class.check_order(ohlc, date=data_index[i + 1])



