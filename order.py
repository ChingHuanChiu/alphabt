from accessor import *
import numpy as np


class Order:
    def __init__(self, unit, limit_price, stop_loss, trading_date=None, is_fill=False, is_parent=True):
        self._unit = unit

        self.limit_price = limit_price
        self.stop_loss = stop_loss
        self.trading_date = trading_date
        self.is_fill = is_fill
        self._is_parent = is_parent

    @property
    def units(self):
        return self._unit

    @units.setter
    def units(self, amount):
        self._unit = amount

    @property
    def is_long(self):
        return self._unit > 0

    @property
    def is_short(self):
        return self._unit < 0

    @property
    def trading_prices(self):
        return self.trading_price

    @trading_prices.setter
    def trading_prices(self, price):
        self.trading_price = price

    @property
    def stop_loss_prices(self):
        return self.stop_loss_price

    @stop_loss_prices.setter
    def stop_loss_prices(self, price):
        self.stop_loss_price = price

    @property
    def is_filled(self):
        """
        check the order is been filled or not
        """
        return self.is_fill

    @is_filled.setter
    def is_filled(self, status):
        self.is_fill = status

    @property
    def is_parents(self):

        if self not in order_execute and order_execute:

            return np.sign(order_execute[-1].units) != np.sign(self.units) or \
                   (position_list[-1] + order_execute[-1].units == 0)
        else:
            return self._is_parent

    def replace(self, amount, trading_price, date, status):

        setattr(self, 'units', amount)
        setattr(self, 'trading_prices', trading_price)
        setattr(self, 'trading_date', date)
        setattr(self, 'is_filled', status)
        self.stop_loss = None

