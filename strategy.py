from abc import ABCMeta, abstractmethod
from broker import Broker
from accessor import position_list
import statistic


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

    def close_position(self):
        """
        close the position when current size of position is not zero
        """
        if position_list[-1] != 0:
            # print("in close", position_list[-1])
            Broker(self.init_capital).make_order(unit=-1 * position_list[-1], limit_price=None, stop_loss=None)
        else:
            pass

    @property
    def empty_position(self):
        return position_list[-1] == 0

    @property
    def long_position(self):
        return position_list[-1] > 0

    @property
    def short_position(self):
        return position_list[-1] < 0



