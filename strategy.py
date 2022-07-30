import pandas as pd

from abc import ABCMeta, abstractmethod

# from alphabt.accessor import Accessor
from alphabt.broker import Broker, Position
from alphabt import taindicator
from alphabt import statistic


class Strategy(metaclass=ABCMeta):

    def __init__(self) -> None:
        self.data = None
        self.init_capital = None


    @abstractmethod
    def signal(self, index):
        """the main strategy logic
        """
        raise NotImplemented

    def buy(self, unit=None, stop_loss=None, stop_profit=None):
        if unit is None:
            
            unit = 0.0001 
        assert unit > 0, f'in buy action, unit must be positive but {unit}'
        Broker.make_order(unit=unit, stop_loss=stop_loss, stop_profit=stop_profit)


    def sell(self, unit=None, stop_loss=None, stop_profit=None):
        if unit is None:
            unit =  -0.0001 
        assert unit < 0 or unit is None, f' in sell action, unit must be negative but {unit}'
        Broker.make_order(unit=unit, stop_loss=stop_loss, stop_profit=stop_profit)
   

    def indicator(self, name, timeperiod=None, return_info: bool=False, **parameters):

        return taindicator.indicator(data=self.data, 
                                     name=name,
                                     timeperiod=timeperiod,
                                     return_info=return_info,
                                     **parameters
        )

        # return statistic.indicator(self.data, name, timeperiod)

    def close_position(self):
        """close the position 
        """
        if Position.status() != 0:
            Broker.make_order(unit=-1 * Position.status(), stop_loss=None, stop_profit=None)
            

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