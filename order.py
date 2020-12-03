
class Order:
    def __init__(self, unit, limit_price, stop_loss, trading_date=None):
        self.unit = unit

        self.limit_price = limit_price
        self.stop_loss = stop_loss
        self.trading_date = trading_date


    @property
    def units(self):
        return self.unit

    @units.setter
    def units(self, unit):
        return unit


    @property
    def is_long(self):
        return self.unit > 0

    @property
    def is_short(self):
        return self.unit < 0

    @property
    def trading_prices(self):
        return self.trading_price

    @trading_prices.setter
    def trading_prices(self, price):
        return price

    def replace(self, unit, trading_price):
        setattr(self, 'unit', unit)
        setattr(self, 'trading_price', trading_price)


