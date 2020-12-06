from accessor import *
class Order:
    def __init__(self, unit, limit_price, stop_loss, trading_date=None, is_trade=False):
        self.unit = unit

        self.limit_price = limit_price
        self.stop_loss = stop_loss
        self.trading_date = trading_date
        self.is_trade = is_trade


    @property
    def units(self):
        return self.unit

    @units.setter
    def units(self, amount):
        self.unit = amount


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
        self.trading_price = price
        
        
    @property
    def stop_loss_prices(self):
        return self. stop_loss_price
    
    @stop_loss_prices.setter
    def stop_loss_prices(self, price):
        self.stop_loss_price = price
        
    @property
    def is_trades(self):
        """
        check the order is been trade or not
        """
        return self.is_trade
    
    @is_trades.setter
    def is_trades(self, status):
        self.is_trade = status

    def replace(self, amount, trading_price, status):
        del order_execute[0] # cancel the old order
        setattr(self, 'units', amount)
        setattr(self, 'trading_prices', trading_price)
        setattr(self, 'is_trades', status)
        order_execute.insert(0, self)


