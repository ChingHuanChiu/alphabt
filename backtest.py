from typing import Tuple, Optional


import pandas as pd


from plot import get_plotly
from alphabt import util
from alphabt.strategy import Strategy
from alphabt.report import Report


from alphabt.order.manager import OrderManager
from alphabt.position.manager import PositionManager
from alphabt.equity.manager import EquityManager
from alphabt.broker.broker import Broker



class Backtest:
    def __init__(self, 
                 strategy: Strategy,
                 initital_equity: float, 
                 commission: Optional[float] = None,
                 tax: Optional[float] = None) -> None:


        self.strategy = strategy
        self.data = util.reset_data(self.strategy.data)
        self.broker = Broker()
        self.broker.position_manager = PositionManager
        self.broker.order_manager = OrderManager
        self.broker.equity_manager = EquityManager(initital_equity,
                                                   commission,
                                                   tax)


    def run(self) -> None:
        
        data_length = self.data.shape[0]

        for index in range(data_length - 1):
            date, _open, high, low, close, volume, ticker = \
                self.data[index]
            
            self.strategy.signal()
            
            self.broker.review_order(current_price=close,
                                     date=date)


        # clean the last position
        if self.broker.position_manager.status != 0:
            self.broker.liquidate_position(price=self.data['close'][-1],
                                           date=self.data['date'][-1])




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
        
    
  


