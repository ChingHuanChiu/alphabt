from abc import ABCMeta, abstractmethod
from broker import Broker, position
import statistic


class Strategy(metaclass=ABCMeta):

    @abstractmethod
    def signal(self, index):
        """
        the main strategy logic
        """

    def buy(self, unit=None, limit_price=None, stop_loss=None, stop_profit=None):
        if unit is None:
            unit = position() if position() != 0 else 0.0001 
        assert unit > 0, f'in buy action, unit must be positive but {unit}'
        Broker(self.init_capital).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss,
                                             stop_profit=stop_profit)

    def sell(self, unit=None, limit_price=None, stop_loss=None, stop_profit=None):
        if unit is None:
            unit = -position() if position() != 0 else -0.0001 
        assert unit < 0 or unit is None, f' in sell action, unit must be negative but {unit}'
        Broker(self.init_capital).make_order(unit=unit, limit_price=limit_price, stop_loss=stop_loss,
                                             stop_profit=stop_profit)

    def indicator(self, name, timeperiod=None):

        return statistic.indicator(self.data, name, timeperiod)

    @property
    def position(self):
        return position()

    def close_position(self):
        """
        close the position when current size of position is not zero
        """
        if position() != 0:
            # print("in close", position_list[-1])
            Broker(self.init_capital).make_order(unit=-1 * position(), limit_price=None, stop_loss=None, stop_profit=None)
        else:
            pass

    @property
    def empty_position(self):
        return position() == 0

    @property
    def long_position(self):
        return position() > 0

    @property
    def short_position(self):
        return position() < 0
    