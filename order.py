class Order:
    def __init__(self, unit, 
                       stop_loss, 
                       stop_profit, 
                       trading_date=None, 
                       is_fill=False, 
                       is_parent=True):

                       
        self._unit = unit

        self.stop_loss = stop_loss
        self.stop_profit = stop_profit
        self.trading_date = trading_date
        self._is_fill = is_fill
        self._is_parent = is_parent
        self._trading_price = None

    @property
    def units(self):
        return self._unit

    @units.setter
    def units(self, amount):
        self._unit = amount

    @property
    def is_long(self):
        return self.units > 0

    @property
    def is_short(self):
        return self.units < 0

    @property
    def trading_price(self):
        return self._trading_price

    @trading_price.setter
    def trading_price(self, price):
        self._trading_price = price

    @property
    def stop_loss_prices(self):
        return self._stop_loss_price

    @stop_loss_prices.setter
    def stop_loss_prices(self, price):
        self._stop_loss_price = price

    @property
    def stop_profit_prices(self):
        return self._stop_profit_price

    @stop_profit_prices.setter
    def stop_profit_prices(self, price):
        self._stop_profit_price = price

    @property
    def is_filled(self):
        """
        check the order is been filled or not
        """
        return self._is_fill

    @is_filled.setter
    def is_filled(self, status):
        self._is_fill = status

    @property
    def is_parents(self):

        return self._is_parent

    @is_parents.setter
    def is_parents(self, status):
        self._is_parent = status

    def replace(self, **kwargs):

        for k, v in kwargs.items():
            self.__dict__[k] = v
