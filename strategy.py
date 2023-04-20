from typing import Union, Optional

from abc import ABCMeta, abstractmethod

# from alphabt.broker import Broker, Position
from alphabt import taindicator
from alphabt import statistic

from order.manager import OrderManager
from position.manager import PositionManager
from broker.broker import Broker

class Strategy(metaclass=ABCMeta):


    def __init__(self) -> None:
        self.data = None
        self.init_capital = None

        self.ticker = None
        self.trading_price = None
        self.trading_date = None


    @abstractmethod
    def signal(self, index: int) -> None:
        """the main strategy logic
           NOTICE: need to super().signal() first when overide this method
        """
        # trading at next day (index+1) if signal appear
        self.ticker = self.data["ticker"][index+1]
        self.trading_price = self.data["close"][index+1]
        self.trading_date = self.data["date"][index+1]


    def long(self, 
             unit: Union[int, float] = None, 
             stop_loss: Optional[float] = None, 
             stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit = 0.0001
        assert unit > 0, f'unit must be positive but {unit} with long action'


        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='long',
                          ticker=self.ticker,
                          trading_price = self.trading_price,
                          trading_date=self.trading_date
                          )


    def short(self, 
             unit: Union[int, float] = None, 
             stop_loss: Optional[float] = None, 
             stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit =  -0.0001 
        assert unit < 0 or unit is None, f' in sell action, unit must be negative but {unit}'

        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='short',
                          ticker=self.ticker
                          )


    def close(self) -> None:
        """close the position 
        """

        Broker.make_order(unit=-1*PositionManager.status(), 
                          action='close',
                          ticker=self.ticker
                          )
   

    def indicator(self, name, timeperiod=None, return_info: bool=False, **parameters):

        return taindicator.indicator(data=self.data, 
                                     name=name,
                                     timeperiod=timeperiod,
                                     return_info=return_info,
                                     **parameters
        )

        # return statistic.indicator(self.data, name, timeperiod)


            

    @property
    def position(self):
        return Position.status()

    @property
    def empty_position(self):
        return Position.status() == 0

    @property
    def long_position(self):
        return Position.status() > 0

    @property
    def short_position(self):
        return Position.status() < 0
    



class Equity:

    _equity = None

    def __init__(self, init_eq) -> None:
        self.equity = init_eq

    @property
    def equity(self) -> float:
        return self._equity

    @equity.setter
    def equity(self, e):
        self.__class__._equity = e