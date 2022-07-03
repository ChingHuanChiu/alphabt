import pandas as pd
from pandas.tseries.offsets import BDay
from typing import Tuple, Optional, Dict

from plot import get_plotly
from broker import *
from alphabt import util
from alphabt.strategy import Strategy, PortfoiloStrategy , Equity
from alphabt.accessor import Accessor
from alphabt.report import Report
from alphabt.data.data import Data



class Backtest:
    """TODO: check type['Self']
    """
    def __new__(cls, strategy, commission=None, **kwargs) :
            if issubclass(strategy, Strategy):
                self = _Bt(strategy=strategy, commission=commission)

            elif issubclass(strategy, PortfoiloStrategy):
                print("It's pedding...")
                self = _PortBt(...)

            return self




class _Bt:
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






class _PortBt:
    def __init__(self, strategy: PortfoiloStrategy, commision: float, stop_loss: float, stop_profit: float) -> None:
        self.strategy = strategy
        self.commision = commision
        self.sl = stop_loss
        self.sp = stop_profit

        Data.datasource = 'yflocal'
        data = Data()
        self._close = data.get_data('close')
        self._open = data.get_data('open')
        self._high = data.get_data('high')
        self._low = data.get_data('low')
        self._vol = data.get_data('volume')

    def run(self):


        for start_date, end_date in self._date_iter_periodicity():
            select_ticker = ['a', 'b']
            _equity_recoder = []
            _log_recoder = []
            tickers_data = self._make_stock_data(select_ticker, start_date, end_date)
            if Equity.equity is None:
                equity = self.strategy.init_equity
            else:
                equity = sum(_equity_recoder)

            equity_per_ticker = self._allocate_equity(equity=equity)
            for _t in select_ticker:
                strategy_class = _bt_factory(stock_data=tickers_data[_t], initial_equity=equity_per_ticker[_t], stop_loss=self.sl, stop_profit=self.sp)
                bt = _Bt(strategy=strategy_class, commission=self.commision)
                bt.run()
                _equity_recoder.append(Equity.equity)
                _log_recoder.append(bt.Broker.get_log())
        
        return _log_recoder # tmp return for testing



                

    def _allocate_equity(self, equity: float, tickers_list: List[str], method: str = 'mean'):
        """TODO: add more allocate method
        """

        if method == 'mean':
            equity_per_ticker = equity // len(tickers_list)
            return {ticker: equity_per_ticker for ticker in tickers_list}



    def _date_iter_periodicity(date_list, hold_days):
        

        date = date_list[0]
        end_date = date_list[-1]
        while date < end_date:
            yield (date), (date + BDay(hold_days))
            date += BDay(hold_days)



    def _make_stock_data(self, tickers_list: List[str], st_date, end_date) -> Dict[str, pd.DataFrame]:

        res = dict()
  
        for ticker in tickers_list:
            sub_data = [self._close[ticker][st_date: end_date], self._open[ticker][st_date: end_date], 
                        self._high[ticker][st_date: end_date], self._low[ticker][st_date: end_date], self._vol[ticker][st_date: end_date]]

            sub_df = pd.concat(sub_data, 1)
            sub_df.columns = ['close', 'open', 'high', 'low', 'vol']
            sub_df['ticker'] = [ticker] * self._close[ticker][st_date: end_date].shape[0]
            res[ticker] = sub_df
        return res




def _bt_factory(stock_data: pd.DataFrame, initial_equity: int, stop_loss: Optional[float], stop_profit: Optional[float]) -> Strategy:
    """factory function for the _PortBt class, 
       the main idea of this class is that giving a range of date of ticker data and doing backtest by signal column

       @stock_data pd.DataFrame : which include: OHLC and  signal, 1 or -1
       @initial_equity int :  initial equity
       @stop_loss Optional[float] : sell the stock when touch the stop loss price
       @stop_profit Optional[float] : sell the stock when touch the stop profit price
    """
    class Pt(Strategy):
        def __init__(self) -> None:
            self.init_capital = initial_equity
            self.data = stock_data

        def signal(self, index):
            if (self.data[index] == 1) & (self.empty_position):
                self.buy(stop_loss=stop_loss, stop_profit=stop_profit)

            if (self.data[index] == -1) & (self.long_position):
                self.close_position()

    return Pt
