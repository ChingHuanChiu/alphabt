from typing import Union, Optional

from abc import ABCMeta, abstractmethod

# from alphabt.broker import Broker, Position
from alphabt import statistic

from alphabt.position.manager import PositionManager
from alphabt.broker.broker import Broker
from alphabt.common.talibindicator import indicator

class Strategy(metaclass=ABCMeta):


    def __init__(self) -> None:
        self.data = None
        self.init_capital = None

        self.ticker = None
        self.entry_price = None
        self.entry_date = None


    @abstractmethod
    def signal(self, index: int) -> None:
        """the main strategy logic
           NOTICE: need to super().signal() first when overide this method
           # TODO: find the way to chechk if the signal method useing 'close' method and 'super().signal'
        """
        # trading at next day (index+1) if signal appear
        self.ticker = self.data["ticker"][index+1]
        self.entry_price = self.data["open"][index+1]
        self.entry_date = self.data["date"][index+1]


    def long(self, 
             unit: Union[int, float] = None, 
             stop_loss: Optional[float] = None, 
             stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit = 1

        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='long',
                          ticker=self.ticker,
                          trading_price = self.entry_price,
                          trading_date=self.entry_date
                          )


    def short(self, 
              unit: Union[int, float] = None, 
              stop_loss: Optional[float] = None, 
              stop_profit: Optional[float] = None) -> None:
        
        if unit is None:
            unit =  -1

        Broker.make_order(unit=unit, 
                          stop_loss=stop_loss, 
                          stop_profit=stop_profit,
                          action='short',
                          ticker=self.ticker,
                          trading_price = self.entry_price,
                          trading_date=self.entry_date
                          )


    def close(self) -> None:
        """close the position 
        """

        Broker.make_order(unit=-1*PositionManager.status(), 
                          action='close',
                          ticker=self.ticker
                          )
   

    def indicator(self, name, timeperiod=None, return_info: bool=False, **parameters):

        return indicator(data=self.data, 
                         ame=name,
                         timeperiod=timeperiod,
                         return_info=return_info,
                         **parameters
        )

            

    @property
    def position(self):
        return PositionManager.status()

    @property
    def empty_position(self):
        return PositionManager.status() == 0

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