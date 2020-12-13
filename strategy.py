from abc import ABCMeta, abstractmethod
from broker import Broker
from accessor import position_list
import  statistic
import pandas as pd


class Strategy(metaclass=ABCMeta):

    @abstractmethod
    def signal(self, index):
        """
        the main strategy logic
        """

    def buy(self, unit=1, limit_price=None, stop_loss=None):

        Broker(self.init_capital).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss)

    def sell(self, unit=-1, limit_price=None, stop_loss=None):

        Broker(self.init_capital).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss)

    def indicator(self, name, timeperiod=None):

        return statistic.indicator(self.data, name, timeperiod)

    @property
    def position(self):
        return position_list[-1]

    @property
    def close_position(self):

        Broker(self.init_capital).make_order(unit=-1 * position_list[-1], limit_price=None, stop_loss=None)


